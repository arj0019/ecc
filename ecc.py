import argparse
from collections import OrderedDict
import logging
import pprint
import re
import shutil


TERMSIZE = shutil.get_terminal_size()  # get the terminal size for formatting


DEL = r'\.del\s+(?P<expr>.+?)(?=\.\w+\s+|$)'
FMT = r'\.fmt\s+(?P<sym>\w+)\s*::=\s*(?P<expr>.*?)(?=\.\w+\s+|$)'
MAP = r'\.map\s+(?P<sym>\w+)\s*::=\s*(?P<expr>.*?)(?=\.\w+\s+|$)'


class Parser():

  def __init__(self, grammar, **kwargs):
    """ Initialize a parser with a given grammar and configuation.

    Args:
      grammar (str): lanugage grammar formatted as BNF+RE
    """
    grammar = re.sub(r'(\n|\t)', '', grammar)

    _del = re.search(DEL, grammar, re.MULTILINE)
    self._del = _del.group('expr') if _del else ''

    sfmt = re.findall(FMT, grammar)
    sfmt = [(sym, re.split(r'\s*\|\s*', expr)) for sym, expr in sfmt]
    self.sfmt = OrderedDict(sfmt)
    logging.info(hformat('GRAMMAR', dict(self.sfmt)))

    smap = re.findall(MAP, grammar)
    smap = [(sym, re.split(r'\s*\|\s*', expr)) for sym, expr in smap]
    self.smap = OrderedDict(smap)
    logging.info(hformat('SYNTAX', dict(self.smap)))

  def parse(self, source):
    """ Parse the given source code into an AST with recursive decent, that is
    translated into an internal representation.

    Args:
      source (str): source code to parse; formatted according to grammar

    Returns:
      ir (list, dict): internal representation of the given source code
    """
    _source = self.preprocess(source)
    ast = Parser._reduce(self._parse(_source, self.sfmt.items()))
    logging.info(hformat('AST', ast))

    ir = self._translate(ast)
    # TODO: -v print internal representation

    return ir

  def preprocess(self, source):
    """Modify given source code according to grammar configuration

    Args:
      self._del (str): characters to exclude
      source (str): source code to preprocess

    Returns:
      source (str): preprocessed source code
    """
    return re.sub(self._del, '', source)  # remove grammar exclusions

  def _parse(self, source, targets):
    """ Parse the given source code into an AST with recursive decent.

    Args:
      source (str): source code to parse; formatted according to grammar
      targets (dict): targeted symbol(s) of recursive decent

    Returns:
      ast (list, dict): abstract syntax tree of the given source code
    """
    ast = [];
    while source:  # sequentially match source to grammar
      for sym, exprs in targets:
        for expr in exprs:
          #print(f"{sym=}, {expr=}, {source=}")  # debug...
          if not (match := re.match(expr, source, re.DOTALL)): continue

          # recursively parse subexpressions (grammar references)
          _ast = {sym: {}}
          try:
            if (_match := match.groupdict().items()):
              for _sym, _expr in _match:
                if not _expr: continue
                _targets = {_sym: self.sfmt[_sym]}.items()
                _ast[sym][_sym] = self._parse(_expr, _targets)
            else:
              _ast[sym] = match.group(0)
            ast.append(_ast); break

          except: continue
        else: continue
        source = source[match.end():]; break

      else: raise SyntaxError(f"@ln:col ({source})")
    return ast

  def _translate(self, ast): return ast

  @staticmethod
  def _reduce(struct):
    """ Recursively reduce nested lists and dictionaries.

    Reduce any list with a single element to that element.
    
    In any dictionary, if the value corresping to a key is a dictionary with
    only one key, and that key is the same as the outer key, reduce the value
    corresonding to the outer key to the value corresponding to the inner key.
    """
    if isinstance(struct, list):
      # recursively reduce lists by element(s)
      _struct = [Parser._reduce(item) for item in struct]

      # if a list has one element, replace it with that element
      if len(_struct) == 1: return _struct[0]
      else: return _struct

    elif isinstance(struct, dict):
      _struct = {}
      for key, value in struct.items():  # Recursively reduce dictionaries by key
        _value = Parser._reduce(value)
        if (isinstance(_value, dict) and len(_value) == 1 and key in _value):
          _struct[key] = _value[key]
        else: _struct[key] = _value
      return _struct

    else: return struct


class Optimizer():
  def __init__(self, **kwargs):
    """ Initialize an optimizer with a given configuration. """

  def optimize(ir): return ir


class Generator(): pass


def hformat(header, body, **kwargs):
  header = f"--- {header} {'-' * (TERMSIZE.columns - len(header) - 5)}\n"
  return header + pprint.pformat(body, sort_dicts=False, **kwargs)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='ecc', description='x86 assembly compilers generated from Backus Naur grammar extended with regular expressions')
  parser.add_argument('grammar', help='language grammar file path')
  parser.add_argument('source', help='source code file path')
  parser.add_argument('-v', '--verbose', default='WARNING',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help="Set the logging level (default: WARNING).")
  args = parser.parse_args()

  logging.basicConfig(level=args.verbose, format=f'%(message)s')

  with open(args.grammar, 'r') as file: _grammar = file.read()
  parser = Parser(_grammar)

  with open(args.source, 'r') as file: source = file.read()
  ast = parser.parse(source)
