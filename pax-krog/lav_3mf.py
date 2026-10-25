"""Pak pax_krog.stl som Bambu Studio-projekt (.3mf) med printer, filament og
printindstillinger bagt ind.  Kør:  python3 lav_3mf.py
"""
import json, uuid, zipfile, datetime
import numpy as np, trimesh

PRINTER  = "Bambu Lab P1S 0.4 nozzle"
PROCESS  = "0.20mm Standard @BBL X1C"      # P1S deler procesprofil med X1C
FILAMENT = "Bambu PETG Basic @BBL X1C"     # kompatibel med P1S 0.4
BED      = "Textured PEI Plate"
PLATE    = 256.0                           # P1S-plade i mm
NAME     = "pax_krog"
OUT      = "pax_krog_P1S_PETG.3mf"
VERSION  = "01.10.01.50"

# Indstillinger der afviger fra "0.20mm Standard": stærk, men stadig hurtig.
OVERRIDES = {
    "layer_height": "0.2",
    "wall_loops": "4",
    "sparse_infill_density": "40%",
    "sparse_infill_pattern": "gyroid",
    "enable_support": "0",
}

m = trimesh.load("pax_krog.stl")
assert m.volume > 0, "normaler vender indad"
assert m.is_watertight
lo, hi = m.bounds
center = (lo + hi) / 2
V = m.vertices - center                  # Bambu gemmer mesh centreret om objektets origo
F = m.faces
h = hi[2] - lo[2]
place = f"1 0 0 0 1 0 0 0 1 {PLATE/2:g} {PLATE/2:g} {h/2:g}"   # midt på pladen, bund på z=0
ident = "1 0 0 0 1 0 0 0 1 0 0 0"
now = datetime.datetime.now().strftime("%Y-%m-%d")
u = lambda: str(uuid.uuid4())

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')

verts = "\n".join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in V)
tris  = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F)
object_model = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" {NS}>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <resources>
  <object id="1" p:UUID="{u()}" type="model">
   <mesh>
    <vertices>
{verts}
    </vertices>
    <triangles>
{tris}
    </triangles>
   </mesh>
  </object>
 </resources>
 <build/>
</model>
"""

main_model = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" {NS}>
 <metadata name="Application">BambuStudio-{VERSION}</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="Copyright"></metadata>
 <metadata name="CreationDate">{now}</metadata>
 <metadata name="Description">Krog til PAX-skuffefront, 17 mm</metadata>
 <metadata name="Designer"></metadata>
 <metadata name="DesignerCover"></metadata>
 <metadata name="DesignerUserId"></metadata>
 <metadata name="License"></metadata>
 <metadata name="ModificationDate">{now}</metadata>
 <metadata name="Origin"></metadata>
 <metadata name="Title">{NAME}</metadata>
 <resources>
  <object id="2" p:UUID="{u()}" type="model">
   <components>
    <component p:path="/3D/Objects/object_1.model" objectid="1" p:UUID="{u()}" transform="{ident}"/>
   </components>
  </object>
 </resources>
 <build p:UUID="{u()}">
  <item objectid="2" p:UUID="{u()}" transform="{place}" printable="1"/>
 </build>
</model>
"""

obj_meta = "\n".join(f'    <metadata key="{k}" value="{v}"/>' for k, v in OVERRIDES.items())
model_settings = f"""<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="{NAME}"/>
    <metadata key="extruder" value="1"/>
{obj_meta}
    <part id="1" subtype="normal_part">
      <metadata key="name" value="{NAME}.stl"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="{NAME}.stl"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="{center[0]:.4f}"/>
      <metadata key="source_offset_y" value="{center[1]:.4f}"/>
      <metadata key="source_offset_z" value="{center[2]:.4f}"/>
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value=""/>
    <metadata key="locked" value="false"/>
    <model_instance>
      <metadata key="object_id" value="2"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="1"/>
    </model_instance>
  </plate>
  <assemble>
   <assemble_item object_id="2" instance_id="0" transform="{place}" offset="0 0 0" />
  </assemble>
</config>
"""

project = {
    "version": VERSION,
    "from": "project",
    "name": NAME,
    "printer_settings_id": PRINTER,
    "printer_model": "Bambu Lab P1S",
    "printer_variant": "0.4",
    "print_settings_id": PROCESS,
    "filament_settings_id": [FILAMENT],
    "filament_type": ["PETG"],
    "curr_bed_type": BED,
    "different_settings_to_system": [";".join(OVERRIDES), "", ""],
    **OVERRIDES,
}

content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
</Types>
"""
rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""
model_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/Objects/object_1.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("3D/3dmodel.model", main_model)
    z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
    z.writestr("3D/Objects/object_1.model", object_model)
    z.writestr("Metadata/model_settings.config", model_settings)
    z.writestr("Metadata/project_settings.config", json.dumps(project, indent=4))
print(f"skrev {OUT}: {len(V)} punkter, {len(F)} trekanter, placeret {place}")
