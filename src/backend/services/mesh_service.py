"""Federated mesh service — exposes the list of monitoring nodes.

In production this would come from a service registry (Consul, etcd) or
the database of provisioned IoT devices.
"""
from models import MeshNode


_NODES: list[MeshNode] = [
    MeshNode(id="SP-BR",  description="São Paulo · Calor Extremo",  kind="risk",    pingMs=12, weightSize="4.2 MB", lat=-23.5, lng=-46.6),
    MeshNode(id="NYC-US", description="New York · Baseline",         kind="normal",  pingMs=22, weightSize="2.1 MB", lat= 40.7, lng=-74.0),
    MeshNode(id="LDN-UK", description="London · Baseline",           kind="normal",  pingMs=18, weightSize="2.0 MB", lat= 51.5, lng= -0.1),
    MeshNode(id="TYO-JP", description="Tokyo · Baseline",            kind="normal",  pingMs=45, weightSize="2.3 MB", lat= 35.6, lng=139.7),
    MeshNode(id="SYD-AU", description="Sydney · Anomalia Térmica",   kind="warning", pingMs=41, weightSize="2.6 MB", lat=-33.8, lng=151.2),
    MeshNode(id="SGP-SG", description="Singapore · Baseline",        kind="normal",  pingMs=33, weightSize="2.2 MB", lat=  1.3, lng=103.8),
    MeshNode(id="MSK-RU", description="Moscow · Baseline",           kind="normal",  pingMs=39, weightSize="2.4 MB", lat= 55.7, lng= 37.6),
    MeshNode(id="CPT-ZA", description="Cape Town · Seca",            kind="warning", pingMs=24, weightSize="2.1 MB", lat=-33.9, lng= 18.4),
    MeshNode(id="DEL-IN", description="Nova Delhi · Inundação",      kind="risk",    pingMs=38, weightSize="3.8 MB", lat= 28.6, lng= 77.2),
    MeshNode(id="BSB-BR", description="Brasília · Baseline",         kind="normal",  pingMs=16, weightSize="2.0 MB", lat=-15.7, lng=-47.9),
    MeshNode(id="MEX-MX", description="Cidade do México · Baseline", kind="normal",  pingMs=28, weightSize="2.1 MB", lat= 19.4, lng=-99.1),
    MeshNode(id="STO-SE", description="Stockholm · Baseline",        kind="normal",  pingMs=20, weightSize="2.0 MB", lat= 59.3, lng= 18.0),
]


def list_nodes() -> list[MeshNode]:
    return list(_NODES)
