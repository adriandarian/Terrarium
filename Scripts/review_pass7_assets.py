"""Serialize native asset capture jobs; each child waits for rendered files."""
import subprocess,sys
assets=sys.argv[1:] or ['SM_MeadowTile_v5','SM_PathTile_v4','SM_GroundPlants_v2','SM_MeadowFlowers_v2','SM_ShoreOutcrop_v2','SM_CliffMoss_v1','SM_GardenBed_v3','SM_PlankBridge_v3','SM_StoneStairs_v3','SM_Traveler_v2']
for asset in assets:
    subprocess.run([sys.executable,'Scripts/capture_pass7_asset.py',asset],check=True)
    print('CAPTURED '+asset,flush=True)
