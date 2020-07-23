import ast
import _ast
from ast import *
from ast_utils import *
from astunparse import unparse
import re


# Class to remove parameter from an API invocation
class KeywordParamRemover(ast.NodeTransformer):
    functionName = ""
    parameterName = ""
    listChanges = []
    list_line_number = []

    def __init__(self, fname, pname, listlinenumber):
        self.functionName = fname
        self.parameterName = pname
        self.list_line_number = listlinenumber
        super().__init__()

    def remove_param(self, node: Call):
        # Function name is correct
        # This first one is easy check to make sure that there is a relevant keyword here
        listKeywordParam = getKeywordArguments(node)
        for keyword in listKeywordParam:
            # print(keyword.arg)
            if keyword == self.parameterName:
                keyword_ast = node.keywords
                for key_ast in keyword_ast:
                    if key_ast.arg == self.parameterName:
                        keyword_ast.remove(key_ast)
                node.keywords = keyword_ast


    def visit_Call(self, node: Call):
        if node.lineno in self.list_line_number:
            self.listChanges.append("Deprecated API detected in line: " + node.lineno.__str__())
            self.listChanges.append("Content: \n" + unparse(node))
            tempString = ""
            self.remove_param(node)
            listScope = recurseScope(node)
            for n in listScope:
                if isinstance(n, _ast.Call):
                    self.remove_param(n)
            self.listChanges.append("Updated content: \n" + unparse(node))
        return node

    def transform(self, tree):
        self.listChanges = []
        self.visit(tree)
        # print("Updated code: ")
        # print_code(tree)
        # print("----------------------------------------------------------------------------------------------------")

class KeywordParamChanger(ast.NodeTransformer):
    functionName = ""
    parameterName = ""
    listChanges = []
    list_line_number = []

    def __init__(self, fname, pname, listlinenumber, new_param_name):
        self.functionName = fname
        self.parameterName = pname
        self.list_line_number = listlinenumber
        self.new_param_name = new_param_name
        super().__init__()

    def change_param(self, node: Call):
        # Function name is correct
        # This first one is easy check to make sure that there is a relevant keyword here
        listKeywordParam = getKeywordArguments(node)
        for keyword in listKeywordParam:
            # print(keyword.arg)
            if keyword == self.parameterName:
                keyword_ast = node.keywords
                for key_ast in keyword_ast:
                    if key_ast.arg == self.parameterName:
                        new_keyword = key_ast
                        new_keyword.arg = self.new_param_name
                        keyword_ast.remove(key_ast)
                        keyword_ast.append(new_keyword)
                node.keywords = keyword_ast

    def visit_Call(self, node: Call):
        if node.lineno in self.list_line_number:
            self.listChanges.append("Deprecated API detected in line: " + node.lineno.__str__())
            self.listChanges.append("Content: \n" + unparse(node))
            tempString = ""
            self.change_param(node)
            listScope = recurseScope(node)
            for n in listScope:
                if isinstance(n, _ast.Call):
                    self.change_param(n)
            self.listChanges.append("Updated content: \n" + unparse(node))
        return node

    def transform(self, tree):
        self.listChanges = []
        self.visit(tree)
        # print("Updated code: ")
        # print_code(tree)
        # print("----------------------------------------------------------------------------------------------------")


# Class to process the change of API parameter default value
#
# dummy_clf = DummyClassifier() (Default value is strategy="stratified"))
#  ->
# dummy_clf = DummyClassifier(strategy="stratified")
class DefaultParamValueTransformer(ast.NodeTransformer):
    functionName = ""
    parameterName = ""
    oldDefaultValue = ""

    def __init__(self, fname, pname, oldvalue):
        self.functionName = fname
        self.parameterName = pname
        self.oldDefaultValue = oldvalue
        super().__init__()

    def default_value_transform(self, node: Call):
        nodeFuncName = getFunctionName(node)
        if nodeFuncName == self.functionName:
            # Function name is correct
            listKeywordParam = getKeywordArguments(node)
            isKeywordExist = False
            for keyword in listKeywordParam:
                # print(ast.dump(keyword))
                # print(keyword.arg)
                if keyword.arg == self.parameterName:
                    isKeywordExist = True
            if not isKeywordExist:
                # If keyword is not exist yet, it means that the old API use the default value which is changed
                # in the new API. Therefore, we need to create a new node
                # print("Keyword not exist")
                newParam = createKeywordParam(self.parameterName, self.oldDefaultValue)
                listKeywordParam.append(newParam)

    def visit_Call(self, node: Call):
        nodeFuncName = getFunctionName(node)
        self.default_value_transform(node)
        listScope = recurseScope(node)
        for n in listScope:
            if isinstance(n, _ast.Call):
                self.default_value_transform(n)
        return node

    def transform(self, tree):
        # print_code(tree)
        self.visit(tree)
        # print(ast.dump(tree))
        print_code(tree)


class ApiNameTransformer(ast.NodeTransformer):
    functionName = ""
    newApiName = ""

    def __init__(self, fname, newname, list_line_number, list_found_api):
        self.list_line_number = list_line_number
        self.oldApiName = fname
        self.newApiName = newname
        self.listChanges = []
        self.found_api = list_found_api
        super().__init__()

    def visit_Call(self, node: Call):
        if node.lineno in self.list_line_number:
            actual_api = {}
            for api in self.found_api:
                # found the actual api
                if api["line_no"] == node.lineno:
                    actual_api = api

            self.listChanges.append("Deprecated API detected in line: " + node.lineno.__str__())
            self.listChanges.append("Content: \n" + unparse(node))
            print("Deprecated API detected in line: " + node.lineno.__str__())
            print("Content: \n" + unparse(node))

            convert_all = True
            api_without_arguments = unparse(node)
            nb_rep = 1
            # Remove the arguments
            while (nb_rep):
                (api_without_arguments, nb_rep) = re.subn(r'\([^()]*\)', '', api_without_arguments)


            excessAPI = actual_api['name'].replace(self.oldApiName, '')

            api_without_arguments = api_without_arguments.replace(excessAPI, '')
            print("THIS IS API WITHOUT ARGUMENTS: " + api_without_arguments)

            if not self.change_whole and len(api_without_arguments.split(".")) > 1:
                # Should also process excess API here?
                print("SPECIAL CHANGEEEE")
                # Change the whole API invocation
                print(ast.dump(node))
                # Find if there are excess API invocation / object

                print("ExcessAPI: " + excessAPI)
                # Case have excess API (e.g. KMeans that is followed by .fit)

                currentApi = unparse(node)
                if len(excessAPI) > 1:
                    first_part_excess = excessAPI.split(".")[1]
                    idx = currentApi.index(first_part_excess)
                    # changed part contain the API invocation without the excess invocation
                    changed_part = currentApi[0:idx - 1]
                else:
                    changed_part = currentApi









                print("THE DIFFERENCE IS HERE")
                print("CHANGED PART:")
                print(changed_part)
                changed_part_without_arg = changed_part
                nb_rep = 1
                while (nb_rep):
                    (changed_part_without_arg, nb_rep) = re.subn(r'\([^()]*\)', '', changed_part_without_arg)
                function_name_only = changed_part_without_arg.split(".")[-1].strip()
                print("THIS IS FUNCTION_NAME ONLY: " + function_name_only)
                print("THIS IS CHANGED PART NEW: " + changed_part)
                index_of_split = changed_part.index(function_name_only)
                prepend_api = changed_part[0:index_of_split]
                need_to_be_modified_api = changed_part[index_of_split:]
                print("THIS IS PREPEND API: " + prepend_api)
                print("THIS IS NEED TO BE MODIFIED: " + need_to_be_modified_api)
                bracket_index = need_to_be_modified_api.index("(")
                modified_name = need_to_be_modified_api[0:bracket_index]
                modified_argument = need_to_be_modified_api[bracket_index:]
                print("MODIFIED NAME: " + modified_name)
                print("MODIFIED ARGUMENT: " + modified_argument)
                modified_name = self.newApiName.split(".")[-1]


                if len(excessAPI) > 1:
                    print("Must process the excess API too")
                    print("TRY AST PARSE")
                    # String processing

                    # Index before the excess API
                    first_part_excess = excessAPI.split(".")[1]
                    idx = currentApi.index(first_part_excess)
                    # changed part contain the API invocation without the excess invocation
                    changed_part = currentApi[0:idx - 1]
                    excess_part = currentApi.replace(changed_part, '')
                    # Find out what is the last part argument by using regex

                    newApi = prepend_api + modified_name + modified_argument + excess_part
                    print("NEW API: " + newApi)
                    parsed_code = ast.parse(newApi, mode="eval")
                    call_node = parsed_code.body
                    node = call_node
                else:
                    newApi = prepend_api + modified_name + modified_argument
                    print("NEW API: " + newApi)
                    parsed_code = ast.parse(newApi, mode="eval")
                    call_node = parsed_code.body
                    node = call_node
            else:
                self.need_to_add_import = True
                # Change the whole API invocation
                # Find if there are excess API invocation / object
                excessAPI = actual_api['name'].replace(self.oldApiName, '')
                # Case have excess API (e.g. KMeans that is followed by .fit)
                if len(excessAPI) > 1:
                    print("Must process the excess API too")
                    print("TRY AST PARSE")
                    # String processing
                    currentApi = unparse(node)
                    # Index before the excess API
                    first_part_excess = excessAPI.split(".")[1]
                    idx = currentApi.index(first_part_excess)
                    # changed part contain the API invocation without the excess invocation
                    changed_part = currentApi[0:idx - 1]
                    excess_part = currentApi.replace(changed_part, '')
                    # Find out what is the last part argument by using regex
                    last_part = changed_part
                    nb_rep = 1
                    while (nb_rep):
                        (last_part, nb_rep) = re.subn(r'\([^()]*\)', '', last_part)
                    last_part = last_part.split(".")[-1]
                    api_arguments = changed_part.split(last_part)[1]
                    newApi = self.newApiName.split(".")[-1] + api_arguments + excess_part
                    parsed_code = ast.parse(newApi, mode="eval")
                    call_node = parsed_code.body
                    node = call_node
                else:
                    print("Simply get the arguments and create new API invocations")
                    positional_arg = node.args
                    keyword_arg = node.keywords
                    context = node.func.ctx
                    newInvocation = ast.Call(func=Name(id=self.newApiName.split(".")[-1], ctx=context), args=positional_arg, keywords=keyword_arg)
                    node = newInvocation


            tempString = ""
            # self.name_transformer(node)
            # listScope = recurseScope(node)
            # for n in listScope:
            #     if isinstance(n, _ast.Call):
            #         self.name_transformer(n)
            # self.listChanges.append("Updated content: \n" + unparse(node))
        return node

    def transform(self, tree):
        # print_code(tree)


        # First check if the change is only at the end or also change the API parent object/class
        # Compare the oldapiname and the newapiname
        split_old = self.oldApiName.split(".")
        split_new = self.newApiName.split(".")
        isParentSame = True
        len_old = len(split_old)
        len_new = len(split_new)
        if len_old != len_new:
            isParentSame = False
        else:
            for i in range(0, len_old - 1):
                if split_old[i] != split_new[i]:
                    isParentSame = False
                    break
        # Check the function name
        if split_old[-1] == split_new[-1]:
            isMethodNameSame = True
        else:
            isMethodNameSame = False

        print("isParentSame: " + isParentSame.__str__())
        print("isMethodSame: " + isMethodNameSame.__str__())

        # Case parent same and method not same = only change the end name of the function
        # Case parent diff = better be safe and create new import and change the whole API invocation
        # This will cause a bug if the parent contains other API invocations (which is unlikely if the parent is changed)


        # Check whether there is any deprecated API first
        # For now, it does not matter whether only the function is change or the fully qualified API name is changed

        # It may cause a bug in case the invoked API is dependent on the parent object/attribute
        # Therefore, if the change is only on the function name which is a part of other API invocation (i.e. not
        # a standalone API invocation, we should just change the name of the API without considering the import
        # since the import will still be exist)

        if len(self.list_line_number) > 0:
            if not isMethodNameSame and isParentSame:
                self.change_whole = False
            else:
                self.change_whole = True
            # Change the whole function
            # Will need to change the import!
            print("change whole function")

            # new parent name
            parent_name = ".".join(split_new[0:-1])
            new_api_name = split_new[-1]

            for node in ast.walk(tree):
                if type(node) == ast.ImportFrom:
                    print(node)
                    print(ast.dump(node))

            # Create the new import statement first
            import_node = ast.ImportFrom(module=parent_name, names=[alias(name=new_api_name, asname=None)], level=0)

            print(ast.dump(tree))
            # add the new import just before the first API invocation for now
            # TODO: Think of better placement of the new import
            print("THIS IS LIST LINE NUMBER")
            print(self.list_line_number.__str__())


            # TODO: Change the API invocation into the new imported name (i.e. new_api_name)
            self.need_to_add_import = False
            self.visit(tree)
            if self.need_to_add_import:
                tree.body.insert(self.list_line_number[0] - 1, import_node)


            print_code(tree)


        # self.visit(tree)
        # print_code(tree)