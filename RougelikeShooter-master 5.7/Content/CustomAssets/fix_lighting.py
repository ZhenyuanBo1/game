"""
Run inside UE5: Tools > Execute Python Script > fix_lighting.py
Restores playable lighting while keeping a moody atmospheric feel.
"""

import unreal

eul = unreal.EditorLevelLibrary

actors = eul.get_all_level_actors()

for actor in actors:
    cls_name = actor.get_class().get_name()

    # Restore directional sun to dim-but-visible cool white
    if cls_name == "DirectionalLight":
        comp = actor.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            comp.set_intensity(2.0)
            comp.set_light_color(unreal.LinearColor(0.6, 0.7, 1.0, 1.0))
        print("  DirectionalLight restored")

    # Restore sky light to a dim ambient
    if cls_name == "SkyLight":
        comp = actor.get_component_by_class(unreal.SkyLightComponent)
        if comp:
            comp.set_intensity(0.4)
        print("  SkyLight restored")

    # Boost any PointLight actors (the ones we added)
    if cls_name == "PointLight":
        comp = actor.get_component_by_class(unreal.PointLightComponent)
        if comp:
            comp.set_intensity(3000)
            comp.set_attenuation_radius(5000)
        print("  PointLight boosted")

    # Unhide the sky sphere so the background isn't a void
    if cls_name in ("BP_Sky_Sphere_C", "SkyAtmosphere"):
        actor.set_actor_hidden_in_game(False)
        print(f"  {cls_name} unhidden")

eul.save_current_level()
print("[fix_lighting] Done! Press Play to test.")
