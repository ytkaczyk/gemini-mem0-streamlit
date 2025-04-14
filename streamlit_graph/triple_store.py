from typing import Set

class Edge:
  """
  https://visjs.github.io/vis-network/docs/network/edges.html
  """
  def __init__(self,
               source,
               target,
               color="#F7A7A6",
               # arrows_to=True,
               # arrows_from=False,
               **kwargs
               ):
    self.source=source
    self.__dict__['from']=source
    self.to=target
    self.color=color
    # self.arrows={"to": arrows_to, "from": arrows_from}
    self.__dict__.update(**kwargs)

  def to_dict(self):
    return self.__dict__

class Node:
  def __init__(self,
              id,
              title=None, # displayed if hovered
              label=None, # displayed inside the node
              link=None, # link to open if double clicked
              color=None,
              shape="dot",
              size=25,
              **kwargs
               ):
    self.id=id
    if not title:
      self.title=id
    else:
     self.title=title
    self.label = label
    self.shape=shape # # image, circularImage, diamond, dot, star, triangle, triangleDown, hexagon, square and icon
    self.size=size
    self.color=color #FDD2BS #F48B94 #F7A7A6 #DBEBC2
    self.__dict__.update(**kwargs)

  def to_dict(self):
    return self.__dict__

  def __eq__(self, other) -> bool:
    return (isinstance(other, self.__class__) and
            getattr(other, 'id', None) == self.id)

  def __hash__(self) -> int:
    return hash(self.id)
  
  from streamlit_agraph.node import Node
from streamlit_agraph.edge import Edge

class Triple:
  def __init__(self, subj: Node, pred: Edge, obj:Node ) -> None:
    self.subj = subj
    self.pred = pred
    self.obj = obj

class TripleStore:
  def __init__(self) ->None:
    self.nodes_set: Set[Node] = set()
    self.edges_set: Set[Edge] = set()
    self.triples_set: Set[Triple] = set()

  def add_triple(self, node1, link, node2, image=""):
    nodeA = Node(id=node1, image=image)
    nodeB = Node(id=node2)
    edge = Edge(source=nodeA.id, target=nodeB.id, title=link)  # linkValue=link
    self.add_triple_base(nodeA, edge, nodeB)
  
  def add_triple_base(self, nodeA: Node, edge: Edge, nodeB: Node):
    triple = Triple(nodeA, edge, nodeB)
    self.nodes_set.update([nodeA, nodeB])
    self.edges_set.add(edge)
    self.triples_set.add(triple)

  def getTriples(self)->Set[Triple]:
    return self.triples_set

  def getNodes(self)->Set[Node]:
    return self.nodes_set

  def getEdges(self)->Set[Edge]:
    return self.edges_set