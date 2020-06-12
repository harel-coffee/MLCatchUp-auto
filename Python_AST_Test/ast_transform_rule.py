import ast
from ast import *
from Python_AST_Test.ast_utils import *


# Class to remove parameter from an API invocation
class KeywordParamRemover(ast.NodeTransformer):
    functionName = ""
    parameterName = ""

    def __init__(self, fname, pname):
        self.functionName = fname
        self.parameterName = pname
        super().__init__()

    def visit_Call(self, node: Call):
        nodeFunction = node.func
        nodeFuncName = node.func.id
        # print(ast.dump(node))
        if nodeFuncName == self.functionName:
            # Function name is correct
            listKeywordParam = node.keywords
            for keyword in listKeywordParam:
                # print(keyword.arg)
                if keyword.arg == self.parameterName:
                    listKeywordParam.remove(keyword)
        return node

    def transform(self, tree):
        print_code(tree)
        self.visit(tree)
        # print(ast.dump(tree))
        print_code(tree)


# Class to process the change of API parameter default value
#
# dummy_clf = DummyClassifier() (Default value is strategy="stratified"))
#  ->
# dummy_clf = DummyClassifier(strategy="stratified")
class DefaultParamValueTransformer(ast.NodeTransformer):
    functionName = ""
    parameterName = ""
    parameterNewValue = ""

    def __init__(self, fname, pname, pvalue):
        self.functionName = fname
        self.parameterName = pname
        self.parameterNewValue = pvalue
        super().__init__()

    def visit_Call(self, node: Call):
        nodeFuncName = node.func.id
        if nodeFuncName == self.functionName:
            # Function name is correct
            listKeywordParam = node.keywords
            isKeywordExist = False
            for keyword in listKeywordParam:
                print(ast.dump(keyword))
                # print(keyword.arg)
                if keyword.arg == self.parameterName:
                    isKeywordExist = True
            if not isKeywordExist:
                # If keyword is not exist yet, it means that the old API use the default value which is changed
                # in the new API. Therefore, we need to create a new node
                print("Keyword not exist")
        return node

    def transform(self, tree):
        print_code(tree)
        self.visit(tree)
        # print(ast.dump(tree))
        print_code(tree)