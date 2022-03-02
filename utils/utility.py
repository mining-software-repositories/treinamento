import subprocess
import os
from pathlib import Path
import plotly.graph_objects as go
import lizard
import json
from pydriller import Repository

# Immprime n linhas da lista fornecida
def print_n(n, list_to_print):
  """
  Print n lines of a list
  @param: int n: amout of lines to print
  @param: list list_to_print: list to print
  @return n lines to print
  """
  i = 1
  for each in list_to_print:
    if i < n:
      print(each)
      i +=1

# Ordena um dicionario por value
def sort_dictionary_by_value(x, reverse=True):
  """
  Sort a dictionary by value 
  @param: dictionary x: a dictionary to sort
  @param: bool reverse: True sort decreasing value from max to min
  @return a sorted dictionary
  """
  return sorted(x.items(), key=lambda kv: kv[1], reverse=reverse)

def run_bash_command(bashCommand):
  """"
  Executa um comando bash
  @param: str bashCommand: comando bash
  @return int result: 0 ok 
  """
  result = 0
  try: 
    subprocess.run(bashCommand, shell=True, executable='/bin/bash')
  except subprocess.CalledProcessError as e:
      print(f'Returned code: {e.returncode}, output: {e.output}')
      result = e.returncode
  return result

def create_file_from_bash_tree(repository_src, filename, all_files_directories=True):
  """
  Cria um arquivo texto a partir da execucao de um comando bash
  @param: str repository_src: src do repositorio que sera analisado
  @param: str all_files_directories: True para gerar todos os arquivos e diretorios
  @param: str filename: nome do arquivo de entrada
  :raises ExceptionType:Exception caso aconteca algum erro
  """
  try: 
    if all_files_directories: 
      bashCommand = f"tree {repository_src} -i -f > {filename}"
    else: 
      bashCommand = f"tree {repository_src} -d -i -f > {filename}"
    if run_bash_command(bashCommand) == 0:
        print(f'File {filename} created successfully!')
    else:
        raise Exception(f"Erro while try to create the file {filename}")
  except Exception as ex:
    print(f'Erro: {ex}')
  return filename

def convert_file_in_list(filename):
    """
    Convert as linhas de um arquivo texto em uma lista com as linhas do arquivo
    Retorna a lista das linhas do arquivo
    @param: str filename: nome do arquivo de entrada
    @return list list_of_lines
    :raises ExceptionType:Exception caso aconteca algum erro
    """
    list_of_lines = []
    try:
        with open(filename) as file:
            for line in file:
                line = line.rstrip("\n")
                list_of_lines.append(line)

            # Remove os dois ultimos elementos
            del list_of_lines[-1]
            del list_of_lines[-1]
    except Exception as ex:
        print(f'Erro: {ex}')
    return list_of_lines

def create_loc_file_from_bash_tree(repository_src, filename):
  """
  Cria um arquivo texto a partir da execucao de um comando bash
  @param: str repository_src: src do repositorio que sera analisado
  @param: str filename: nome do arquivo de entrada
  :raises ExceptionType:Exception caso aconteca algum erro
  """
  try: 
    bashCommand = f"find {repository_src} -name *.java | xargs wc -l > {filename}"
    if run_bash_command(bashCommand) == 0:
        print(f'File {filename} created successfully!')
    else:
        raise Exception(f'Erro while try to create the file {filename}')
  except Exception as ex:
    print(f'Erro: {ex}')
  return filename

# Lista com LoCs de cada arquivo: (loc, arquivo)
def generate_list_locs_files(repository, filename):
    """
    Cria uma lista de loc por arquivo a partir de um arquivo de locs e files
    @param: str repository: src do repositorio que sera analisado
    @param: str filename: nome do arquivo de entrada
    """
    list_locs_files = []
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if repository in line:
                    line = line.split(' ')
                    elemento = line[0], line[1]
                    list_locs_files.append(elemento)
    except Exception as ex:
        print(f'Erro: {ex}')
    return list_locs_files

# Pega a complexidade ciclomatica maxima de um arquivo (classe) analisado
def get_max_cyclomatic_complexity(filename_with_path):
  """
  Get max cyclomatic complexity of class based on cyclomatic complexity method
  @param: str filename_with_path: filename with full path
  @return max cyclomatic complexity of filename
  """
  file_to_analyse = lizard.analyze_file(filename_with_path)
  cc = 1
  list_temp = []
  if len(file_to_analyse.function_list) > 0:
    for each in file_to_analyse.function_list:
      list_temp.append( each.__dict__['cyclomatic_complexity'] )
    cc = max(list_temp)
  return cc

def search_loc_of_file(file_name, list):
  """
  Para cada arquivo procura sua LOC (Lines of Code)
  @param: str file_name: nome do arquivo
  @param: str list: lista contendo todos os arquivos do projeto
  @return int Loc: do arquivo dado
  """
  for each in list:
    if file_name in each[1]:
      return int(each[0])

def generate_list_cc_files(list_locs_files):
    # Lista com CCs de cada arquivo: (cc, arquivo)
    list_cc_files = []
    for each in list_locs_files:
        filename_with_path = each[1]
        cc = get_max_cyclomatic_complexity(filename_with_path)
        elemento = (cc, filename_with_path)
        list_cc_files.append(elemento)  
    return list_cc_files

# Dicionario com o LoC de cada arquivo
def create_dicionario_loc_filename(lista):
    dicionario = {}
    for item in lista:
        loc = item[0]
        name = item[1].split('/')[-1]
        dicionario[name] = int(loc)
    return dicionario

# Dicionario com a frequencia de commits de cada arquivo
def create_dicionario_fc_filename(dicionario_fc):
    dicionario = {}
    for k, v in dicionario_fc.items():
      dicionario[k] = len(v)
    return dicionario

def concat_str(str1, str2):
    temp = str1 + ',' + str2
    return temp

def convert_list_to_str(lista):
    temp = ''
    if len(lista) > 0:
        temp = ','.join( str(v) for v in lista)
    return temp

def convert_modifield_list_to_str(lista):
    list_aux = []
    for each in lista:
        list_aux.append(each.filename)
    str = convert_list_to_str(list_aux)
    return str

def convert_dictionary_to_str(dictionary):
    temp = ''
    if len(dictionary) > 0:
        temp = str(json.dumps(dictionary))
    return temp

def list_commits_between_tags(from_tag, to_tag, my_repository):
    list_temp = []
    for commit in Repository(my_repository, from_tag=from_tag, to_tag=to_tag).traverse_commits():
        list_temp.append(commit)
    return list_temp