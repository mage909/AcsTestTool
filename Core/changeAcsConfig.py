'''
Created on Feb 5, 2015

@author: jenkins
'''
from xml.etree.ElementTree import ElementTree


def modify_sn(path_xml, sn):
    tree = ElementTree()
    root = tree.parse(path_xml)
    paras = root.findall("Phones/Phone/Parameter")
    paraSN = paras[1]
    paraSN.set("value", sn)
    tree.write(path_xml, encoding="utf-8", xml_declaration=True)
if __name__ == "__main__":
    modify_sn("acs/_ExecutionConfig/Bench_live.xml", "123123123123")
