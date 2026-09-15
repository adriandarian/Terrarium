import sys,importlib
sys.path.insert(0,'C:/Users/hello/Projects/Terrarium/Scripts/BlenderRebuild')
import moss_cap
importlib.reload(moss_cap)
result=moss_cap.build('MossFringe',fringe=True)
