import os
import shutil

import javalang


def get_class_name(tree):
    """
    Obtém o nome da classe Java no código fornecido.
    """
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            return node.name
    return None


def extract_fields(node):
    """
    Extrai os campos (fields) de uma classe Java.
    """
    fields = []
    for field_declaration in node.fields:
        field_type = field_declaration.type.name
        field_name = field_declaration.declarators[0].name
        fields.append(f"private final {field_type} {field_name};")
    return fields


def get_method_start_end(method_node, tree):
    """
    Obtém a posição de início e fim de um método na árvore de análise.
    """
    startpos = None
    endpos = None
    startline = None
    endline = None

    # Itera sobre a árvore de análise para encontrar o início e o fim do método
    for path, node in tree:
        # Se o início foi encontrado e o método atual não está no caminho
        if startpos is not None and method_node not in path:
            # Atribui a posição de término e a linha de término
            endpos = node.position
            endline = node.position.line if node.position is not None else None
            break

        # Se o início ainda não foi encontrado e o nó atual é o método em questão
        if startpos is None and node == method_node:
            # Atribui a posição de início e a linha de início
            startpos = node.position
            startline = node.position.line if node.position is not None else None

    return startpos, endpos, startline, endline


def get_method_text(startpos, endpos, startline, endline, last_endline_index, codelines):
    """
    Obtém o texto do método Java.
    """
    if startpos is None:
        return "", None, None, None
    else:
        startline_index = startline - 1
        endline_index = endline - 1 if endpos is not None else None

        # Verifica e recupera anotações, ajustando o início da linha se necessário
        if last_endline_index is not None:
            for line in codelines[(last_endline_index + 1):(startline_index)]:
                if "@" in line:
                    startline_index = startline_index - 1

        # Obtém o texto do método e mantém as chaves {}
        meth_text = "<ST>".join(codelines[startline_index:endline_index])
        meth_text = meth_text[:meth_text.rfind("}") + 1]

        # Remove chaves e conteúdo externo/comentários indesejados
        if not abs(meth_text.count("}") - meth_text.count("{")) == 0:
            brace_diff = abs(meth_text.count("}") - meth_text.count("{"))
            for _ in range(brace_diff):
                meth_text = meth_text[:meth_text.rfind("}")]
                meth_text = meth_text[:meth_text.rfind("}") + 1]

        # Formata o texto do método e as linhas
        meth_lines = meth_text.split("<ST>")
        meth_text = "".join(meth_lines)
        last_endline_index = startline_index + (len(meth_lines) - 1)

        return meth_text, (startline_index + 1), (last_endline_index + 1), last_endline_index


def get_method(name, tree, codelines):
    """
    Obtém o texto do método Java pelo nome.
    """
    lex = None
    # Filtra e processa os métodos encontrados na árvore de análise
    for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
        startpos, endpos, startline, endline = get_method_start_end(method_node, tree)
        method_text, startline, endline, lex = get_method_text(startpos, endpos, startline, endline, lex, codelines)
        if method_node.name == name:
            return method_text


def get_method_signature(name, tree, codelines):
    """
    Obtém a assinatura do método Java pelo nome.
    """
    lex = None
    # Filtra e processa os métodos encontrados na árvore de análise
    for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
        startpos, endpos, startline, endline = get_method_start_end(method_node, tree)
        method_text, startline, endline, lex = get_method_text(startpos, endpos, startline, endline, lex, codelines)
        if method_node.name == name:
            return format_method_signature(method_text)


def format_method_signature(method_text):
    result = method_text.split('\n')
    for index, line in enumerate(result):
        if line.strip().startswith("public"):
            return result[index].replace("public ", "").replace("{", ";")


def remove_destination_folder(destination_path):
    """
    Remove o diretório de destino se existir.
    """
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)


def get_java_files(source_path):
    """
    Retorna uma lista dos arquivos .java no diretório de origem.
    """
    java_files = []
    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def get_package_name_and_class_name(code):
    """
    Extrai o nome do pacote e o nome da classe Java a partir do código fonte.
    """
    tree = javalang.parse.parse(code)
    package_name = None
    class_name = get_class_name(tree)

    for path, node in tree.filter(javalang.tree.PackageDeclaration):
        package_name = node.name

    return package_name, class_name


def extract_dependencies(node):
    """
    Extrai as dependências (campos) da classe Java.
    """
    dependencies = []
    for field in node.fields:
        field_type = field.type.name
        field_name = field.declarators[0].name
        dependencies.append({'type': field_type, 'name': field_name})
    return dependencies


def process_java_file(source_file):
    """
    Processa um arquivo .java.
    """
    with open(source_file, 'r') as f:
        codelines = f.readlines()
        code = ''.join(codelines)

    package_name, class_name = get_package_name_and_class_name(code)
    tree = javalang.parse.parse(code)
    return package_name, class_name, tree, codelines

def extract_imports(tree):
    """
    Extrai os imports de uma classe Java.
    """
    imports = []
    for _, node in tree.filter(javalang.tree.Import):
        imports.append(node.path)

    return imports