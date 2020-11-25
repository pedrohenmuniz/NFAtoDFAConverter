# Lucas Augusto Muller - 201665508B
# Pedro Henrique Muniz - 201665520B

from xml.dom import minidom
import xml.etree.cElementTree as ET
import sys

DEBUG_MODE = False # Set it to True for printing infos
FILENAME = 'afn01' # Filename to be read (must be inside "input" folder)

def readInput():
  print('Reading {}.xml'.format(FILENAME))
  try:
    doc = minidom.parse('./input/{}.xml'.format(FILENAME))
  except:
    sys.exit('Error reading {}.xml'.format(FILENAME))

  dfaSymbols = [] # DFA Symbols
  dfaStates = [] # DFA States
  q = [] # DFA States

  nfaTransitions = {} # NFA Transitions
  nfaFinals = [] # NFA Final states

  # Read symbols
  symbols = doc.getElementsByTagName('simbolos')
  for symbol in symbols:
    elements = symbol.getElementsByTagName('elemento')
    print('Alphabet Symbols ({})'.format((len(elements)))) if DEBUG_MODE else None
    for elem in elements:
      dfaSymbols.append(elem.getAttribute('valor'))
      print(elem.getAttribute('valor')) if DEBUG_MODE else None

  # Read states
  states = doc.getElementsByTagName('estados')
  for state in states:
    elements = state.getElementsByTagName('elemento')
    # dfaStatesSize = 2 ** len(elements)
    print('NFA States ({})'.format((len(elements)))) if DEBUG_MODE else None
    for elem in elements:
      dfaStates.append(elem.getAttribute('valor'))
      print(elem.getAttribute('valor')) if DEBUG_MODE else None

  # Read final states
  finalStates = doc.getElementsByTagName('estadosFinais')
  for finalState in finalStates:
    elements = finalState.getElementsByTagName('elemento')
    print('NFA Final States ({})'.format((len(elements)))) if DEBUG_MODE else None
    for elem in elements:
      nfaFinals.append(elem.getAttribute('valor'))
      print(elem.getAttribute('valor')) if DEBUG_MODE else None

  # Read transitions
  transitions = doc.getElementsByTagName('funcaoPrograma')
  for transition in transitions:
    elements = transition.getElementsByTagName('elemento')
    print('NFA Transitions ({})'.format((len(elements)))) if DEBUG_MODE else None
    for elem in elements:
      # If key already exists, appends destiny
      if (elem.getAttribute('origem'), elem.getAttribute('simbolo')) in nfaTransitions:
        nfaTransitions[elem.getAttribute('origem'), elem.getAttribute('simbolo')].append(elem.getAttribute('destino'))
      else: # Creates new key
        nfaTransitions[elem.getAttribute('origem'), elem.getAttribute('simbolo')] = [elem.getAttribute('destino')]
      print('({},{},{})'.format(elem.getAttribute('origem'), elem.getAttribute('simbolo'), elem.getAttribute('destino'))) if DEBUG_MODE else None

  # Read initial state
  initialState = doc.getElementsByTagName('estadoInicial')[0]
  print('FNA Initial States (1)') if DEBUG_MODE else None
  q.append((initialState.getAttribute('valor'),))
  print(initialState.getAttribute('valor')) if DEBUG_MODE else None

  return q, nfaTransitions, nfaFinals, dfaSymbols, dfaStates

def nfaToDfa(q, nfaTransitions, nfaFinals, dfaSymbols):
  dfaTfunc = [] # DFA Transition function
  dfaFinal = [] # DFA Sinal states
  dfaTransitions = {}

  print('Converting NFA to DFA')
  # For each q' state, add the possible set of states for each input (initially q0 contains the DFA initial state)
  for inState in q:
    print("inState: {}".format(inState))
    for symbol in dfaSymbols:
      # State already exists in DFA
      if len(inState) == 1 and (inState[0], symbol) in nfaTransitions:
        dfaTransitions[(inState, symbol)] = nfaTransitions[(inState[0], symbol)]
        if tuple(dfaTransitions[(inState, symbol)]) not in q:
            q.append(tuple(dfaTransitions[(inState, symbol)]))
      # States will be the union of all possible states for each input symbol
      else:
        dest = []
        fDest =[]
        # Return states that can be reached by inState consuming input symbol
        for nState in inState:
          if (nState, symbol) in nfaTransitions and nfaTransitions[(nState, symbol)] not in dest:
              dest.append(nfaTransitions[(nState, symbol)])
        if dest:
          for d in dest:
              for value in d:
                  if value not in fDest:
                      fDest.append(value)
          dfaTransitions[(inState, symbol)] = fDest 
          # New NFA state found that is not in q
          if tuple(fDest) not in q: 
              q.append(tuple(fDest))
  
  # Converts dictionary form to lists
  # Organize DFA final states in a given way | [q1, "a", [q1,q2], ...]
  for key, value in dfaTransitions.items():
    temp_list = [[key[0], key[1], value]]
    dfaTfunc.extend(temp_list)

  # NFA final states F' will be all NFA states containing DFA final state F
  for q_state in q:
    for f_state in nfaFinals:
        if f_state in q_state:
            dfaFinal.append(q_state)


  if DEBUG_MODE:
    print('dfaSymbols: {}'.format(dfaSymbols))
    print('dfaFinal: {}'.format(dfaFinal))
    print('initialState: {}'.format(q[0]))
    print('Dfa transitions')
    for tFunc in dfaTfunc:
      print(tFunc)

  # Organize DFA states
  dfaStatesPrint = []
  for tFunc in dfaTfunc:
    state = ''
    for c in sorted(tFunc[0]):
      state += c
    dfaStatesPrint.append(state)
  dfaStatesPrint = sorted(list(set(dfaStatesPrint)))
  print('dfaStatesPrint: {}'.format(dfaStatesPrint)) if DEBUG_MODE else None

  # Organize DFA initial state
  initialStatePrint = ''
  for c in q[0]:
    initialStatePrint += c
  print('initialStatePrint: {}'.format(initialStatePrint)) if DEBUG_MODE else None
  
  # Organize DFA transitions
  dfaTransitionsPrint = []
  for elem in dfaTfunc:
    origin = ''
    destiny = ''
    for c in sorted(elem[0]):
      origin += c
    for c in sorted(elem[2]):
      destiny += c
    symbol = elem[1]
    dfaTransitionsPrint.append([origin, symbol, destiny])
  print('dfaTransitionsPrint: {}'.format(dfaTransitionsPrint)) if DEBUG_MODE else None

  
  dfaFinalsPrint = []
  for finalState in dfaFinal:
    state = ''
    for c in sorted(finalState):
      state += c
    dfaFinalsPrint.append(state)
  print('dfaFinalsPrint: {}'.format(dfaFinalsPrint)) if DEBUG_MODE else None


  print('Writing DFA')
  writeOutput(q, dfaSymbols, dfaStatesPrint, dfaFinalsPrint, dfaTransitionsPrint, initialStatePrint)

def writeOutput(q, dfaSymbols, dfaStates, dfaFinals, dfaTfunc, initialState):
  # Create xml file
  # Creates DFA level
  root = ET.Element('AFD')

  # Creates symbols level
  doc = ET.SubElement(root, 'simbolos')
  for symbol in dfaSymbols:
    ET.SubElement(doc, 'elemento', valor=symbol)

  # Creates states level
  doc = ET.SubElement(root, 'estados')
  for state in dfaStates:
    ET.SubElement(doc, 'elemento', valor=state)

  # Creates final states level
  doc = ET.SubElement(root, 'estadosFinais')
  for finalState in dfaFinals:
    # ET.SubElement(doc, 'elemento', valor=finalState[-1].replace('q', 'p'))
    ET.SubElement(doc, 'elemento', valor=finalState)

  # Creates transitions level
  doc = ET.SubElement(root, 'funcaoPrograma')
  for elem in dfaTfunc:
    ET.SubElement(doc, 'elemento', origem=elem[0], simbolo=elem[1], destino=elem[2])

  # Creates intial state level
  doc = ET.SubElement(root, 'estadoInicial', valor=initialState)
  
  # Write it
  tree = ET.ElementTree(root)
  tree.write('./output/out_{}.xml'.format(FILENAME.replace('afn', 'afd')))

if __name__ == '__main__':
  q, nfaTransitions, nfaFinals, dfaSymbols, dfaStates = readInput()
  nfaToDfa(q, nfaTransitions, nfaFinals, dfaSymbols)
