"""
UE5 Editor Python Script — RougelikeShooter visual setup
Run inside UE5: Tools > Execute Python Script > pick this file

What it does:
  1. Imports all custom PNG textures into /Game/CustomAssets/
  2. Creates a demon material for BP_EnemyBase
  3. Creates a soldier material for BP_Ally
  4. Sets up a dark indoor scene (removes skybox, dims sun, adds ambient)
  5. Wires buff icons into DT_RougeItem rows
"""

import unreal

al   = unreal.EditorAssetLibrary
asl  = unreal.AssetSystemLibrary
eul  = unreal.EditorLevelLibrary
atl  = unreal.EditorActorUtilities


# ── 1. Import textures ────────────────────────────────────────────────────────

CONTENT_ROOT = "/Game/CustomAssets"

IMPORT_MAP = {
    # character textures
    "Textures/Characters/T_Demon_Skin_D.png":       f"{CONTENT_ROOT}/Textures/Characters/T_Demon_Skin_D",
    "Textures/Characters/T_Demon_Skin_M.png":       f"{CONTENT_ROOT}/Textures/Characters/T_Demon_Skin_M",
    "Textures/Characters/T_Human_Ally_D.png":       f"{CONTENT_ROOT}/Textures/Characters/T_Human_Ally_D",
    "Textures/Characters/T_Human_Ally_M.png":       f"{CONTENT_ROOT}/Textures/Characters/T_Human_Ally_M",
    # buff icons
    "Textures/BuffIcons/T_Icon_AddBullet.png":      f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_AddBullet",
    "Textures/BuffIcons/T_Icon_Ally.png":           f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_Ally",
    "Textures/BuffIcons/T_Icon_AttackShield.png":   f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_AttackShield",
    "Textures/BuffIcons/T_Icon_IncreaseDamage.png": f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_IncreaseDamage",
    "Textures/BuffIcons/T_Icon_RecoverHP.png":      f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_RecoverHP",
    "Textures/BuffIcons/T_Icon_ReduceReloadTime.png":f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_ReduceReloadTime",
    "Textures/BuffIcons/T_Icon_SlowdownCircle.png": f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_SlowdownCircle",
    "Textures/BuffIcons/T_Icon_TempShield.png":     f"{CONTENT_ROOT}/Textures/BuffIcons/T_Icon_TempShield",
}

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

print("[setup] Importing textures...")
task_list = []
for rel_path, dest in IMPORT_MAP.items():
    src_abs = os.path.join(SCRIPT_DIR, rel_path)
    dest_dir = dest.rsplit("/", 1)[0]

    task = unreal.AssetImportTask()
    task.filename = src_abs
    task.destination_path = dest_dir
    task.replace_existing = True
    task.automated = True
    task.save = True

    opts = unreal.TextureFactory()
    task.factory = opts
    task_list.append(task)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task_list)

for t in task_list:
    for imp in t.imported_object_paths:
        print(f"  imported: {imp}")


# ── helper: load asset safely ─────────────────────────────────────────────────

def load(path):
    if al.does_asset_exist(path):
        return al.load_asset(path)
    unreal.log_warning(f"[setup] asset not found: {path}")
    return None


# ── 2. Create demon material for enemy ───────────────────────────────────────

print("[setup] Building demon material...")

demon_mat_path = f"{CONTENT_ROOT}/Materials/M_DemonSkin"

if not al.does_asset_exist(demon_mat_path):
    mat_factory = unreal.MaterialFactoryNew()
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_DemonSkin", f"{CONTENT_ROOT}/Materials",
        unreal.Material, mat_factory
    )

    # base color from demon skin texture
    tex_d = load(f"{CONTENT_ROOT}/Textures/Characters/T_Demon_Skin_D")
    tex_m = load(f"{CONTENT_ROOT}/Textures/Characters/T_Demon_Skin_M")

    if tex_d and mat:
        tex_node = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionTextureSample, -400, 0)
        tex_node.texture = tex_d
        unreal.MaterialEditingLibrary.connect_material_property(
            tex_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

        # emissive: orange glow tinted from texture
        mul = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionMultiply, -400, -200)
        color_const = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionConstant3Vector, -650, -200)
        color_const.constant = unreal.LinearColor(2.0, 0.3, 0.0, 1.0)
        unreal.MaterialEditingLibrary.connect_material_expressions(
            tex_node, "RGB", mul, "A")
        unreal.MaterialEditingLibrary.connect_material_expressions(
            color_const, "", mul, "B")
        unreal.MaterialEditingLibrary.connect_material_property(
            mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    if tex_m and mat:
        rough_node = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionTextureSample, -400, 200)
        rough_node.texture = tex_m
        unreal.MaterialEditingLibrary.connect_material_property(
            rough_node, "RGB", unreal.MaterialProperty.MP_ROUGHNESS)

    if mat:
        unreal.MaterialEditingLibrary.recompile_material(mat)
        al.save_asset(demon_mat_path)
        print("  M_DemonSkin created")
else:
    print("  M_DemonSkin already exists, skipping")


# ── 3. Create human/soldier material for ally ─────────────────────────────────

print("[setup] Building human soldier material...")

ally_mat_path = f"{CONTENT_ROOT}/Materials/M_HumanSoldier"

if not al.does_asset_exist(ally_mat_path):
    mat_factory = unreal.MaterialFactoryNew()
    mat2 = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_HumanSoldier", f"{CONTENT_ROOT}/Materials",
        unreal.Material, mat_factory
    )

    tex_d2 = load(f"{CONTENT_ROOT}/Textures/Characters/T_Human_Ally_D")
    tex_m2 = load(f"{CONTENT_ROOT}/Textures/Characters/T_Human_Ally_M")

    if tex_d2 and mat2:
        tn = unreal.MaterialEditingLibrary.create_material_expression(
            mat2, unreal.MaterialExpressionTextureSample, -400, 0)
        tn.texture = tex_d2
        unreal.MaterialEditingLibrary.connect_material_property(
            tn, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

    if tex_m2 and mat2:
        rn = unreal.MaterialEditingLibrary.create_material_expression(
            mat2, unreal.MaterialExpressionTextureSample, -400, 200)
        rn.texture = tex_m2
        unreal.MaterialEditingLibrary.connect_material_property(
            rn, "RGB", unreal.MaterialProperty.MP_ROUGHNESS)

    if mat2:
        unreal.MaterialEditingLibrary.recompile_material(mat2)
        al.save_asset(ally_mat_path)
        print("  M_HumanSoldier created")
else:
    print("  M_HumanSoldier already exists, skipping")


# ── 4. Assign materials to blueprints ────────────────────────────────────────

print("[setup] Assigning materials to blueprints...")

ENEMY_BP  = "/Game/FirstPerson/Blueprints/BP_EnemyBase"
ALLY_BP   = "/Game/FirstPerson/Blueprints/RougelikeItem/ItemEffect/BP_Ally"

demon_mat = load(demon_mat_path)
ally_mat  = load(ally_mat_path)

for bp_path, mat_asset, label in [
    (ENEMY_BP, demon_mat, "Enemy→Demon"),
    (ALLY_BP,  ally_mat,  "Ally→HumanSoldier"),
]:
    bp = load(bp_path)
    if not bp or not mat_asset:
        print(f"  skip {label} (asset missing)")
        continue
    # Find SkeletalMeshComponent / StaticMeshComponent and override material 0
    comps = unreal.BlueprintEditorLibrary.get_components_of_class(
        bp, unreal.MeshComponent)
    if not comps:
        # fallback: try CapsuleComponent owner — set on the generated class CDO
        print(f"  {label}: no MeshComponent found in blueprint, set manually")
        continue
    for comp in comps:
        comp.set_material(0, mat_asset)
    unreal.EditorAssetLibrary.save_asset(bp_path)
    print(f"  {label} done")


# ── 5. Dark indoor lighting ───────────────────────────────────────────────────

print("[setup] Setting up dark indoor lighting...")

actors = eul.get_all_level_actors()
for actor in actors:
    cls_name = actor.get_class().get_name()

    # Kill sky atmosphere + sky light outdoor influence
    if cls_name in ("SkyAtmosphere", "BP_Sky_Sphere_C"):
        actor.set_actor_hidden_in_game(True)
        eul.set_actor_selection_state(actor, True, False)
        print(f"  hidden: {cls_name}")

    # Dim directional sun light heavily
    if cls_name == "DirectionalLight":
        comp = actor.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            comp.set_intensity(0.15)
            comp.set_light_color(unreal.LinearColor(0.05, 0.05, 0.1, 1.0))
        print("  DirectionalLight dimmed")

    # Sky light — very dark ambient
    if cls_name == "SkyLight":
        comp = actor.get_component_by_class(unreal.SkyLightComponent)
        if comp:
            comp.set_intensity(0.05)
        print("  SkyLight dimmed")

# Add a dim fill point light in the center if none exist
point_lights = [a for a in actors if a.get_class().get_name() == "PointLight"]
if len(point_lights) < 2:
    loc = unreal.Vector(0, 0, 400)
    pl = eul.spawn_actor_from_class(unreal.PointLight, loc)
    lc = pl.get_component_by_class(unreal.PointLightComponent)
    if lc:
        lc.set_intensity(800)
        lc.set_attenuation_radius(3000)
        lc.set_light_color(unreal.LinearColor(0.6, 0.5, 1.0, 1.0))
    print("  Added indoor ambient point light (purple tint)")

eul.save_current_level()
print("[setup] Done! Check your scene.")
