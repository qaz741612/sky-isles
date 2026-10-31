import os, math, json, sys
import numpy as np
import trimesh
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from build_industry_c_v2 import COL, rgba
OUT=os.path.dirname(os.path.abspath(__file__))
sc=trimesh.load(os.path.join(OUT,'C_IndustryYouth_V2_DesignReference.glb'),force='scene',process=False)
print('mesh count',len(sc.geometry),'faces',sum(len(m.faces) for m in sc.geometry.values()))
ren=vtk.vtkRenderer();ren.GradientBackgroundOn();ren.SetBackground(.69,.79,.85);ren.SetBackground2(.95,.89,.84)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetMultiSamples(8);win.SetAlphaBitPlanes(1)
ren.SetUseDepthPeeling(True);ren.SetMaximumNumberOfPeels(70);ren.SetOcclusionRatio(.1)
try:ren.UseFXAAOn()
except:pass
cam=ren.GetActiveCamera();cam.SetViewUp(0,1,0);cam.ParallelProjectionOn()
actors=[]
for name,mesh in sc.geometry.items():
 v=np.asarray(mesh.vertices,dtype=np.float32);f=np.asarray(mesh.faces,dtype=np.int64);
 p=vtk.vtkPolyData();pt=vtk.vtkPoints();pt.SetData(numpy_to_vtk(v,deep=True));p.SetPoints(pt)
 cell=vtk.vtkCellArray();conn=np.column_stack([np.full(len(f),3),f]).reshape(-1)
 cell.SetCells(len(f),numpy_to_vtkIdTypeArray(conn.astype(np.int64),deep=True));p.SetPolys(cell)
 norm=vtk.vtkPolyDataNormals();norm.SetInputData(p);norm.SplittingOff();norm.AutoOrientNormalsOff();norm.ComputePointNormalsOn();norm.ComputeCellNormalsOff();norm.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort());mapper.ScalarVisibilityOff()
 actor=vtk.vtkActor();actor.SetMapper(mapper)
 prop=actor.GetProperty();c=rgba(name);prop.SetColor(*(np.array(c[:3])/255));prop.SetOpacity(c[3]/255)
 prop.SetAmbient(.26 if name.startswith('glass') else .18);prop.SetDiffuse(.82);prop.SetSpecular(.14 if name not in ['glass','glass_light','glass_shadow','solar'] else .53);prop.SetSpecularPower(28 if name in ['glass','glass_light','solar'] else 10)
 if name in ['glass','glass_light','glass_shadow']:prop.SetOpacity(.65 if name!='glass_shadow' else .82)
 ren.AddActor(actor);actors.append((actor,norm,p))

# Soft layered illumination, material colors kept vivid but not flat
for pos,color,intensity in [((-40,65,-35),(1.0,.91,.77),1.32),((35,48,35),(.77,.86,1.0),.72),((-15,17,60),(1.,.91,.90),.45)]:
 light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos);light.SetFocalPoint(0,0,0);light.SetColor(*color);light.SetIntensity(intensity);ren.AddLight(light)
ren.SetAmbient(.20,.2,.2)
try:
 step=vtk.vtkRenderStepsPass();ssa=vtk.vtkSSAOPass();ssa.SetDelegatePass(step);ssa.SetRadius(1.6);ssa.SetBias(.08);ssa.SetKernelSize(96);ssa.SetBlur(True);ren.SetPass(ssa)
except Exception as e:print('tone map unavailable',str(e)[:80])
views={
 '01_hero':((-30,22,-29),(0,-.2,0),27),
 '02_overview':((-28,43,32),(0,-.2,0),31),
 '03_top':((0,55,-.001),(0,0,0),28),
 '04_north':((0,15,-50),(0,0,0),29),
 '05_south':((0,14,51),(0,0,0),29),
 '06_west':((-52,17,0),(0,0,0),30),
 '07_east':((53,18,0),(0,0,0),30),
 '08_workshop_detail':((-15,15,-12),(7.3,1.2,1),13),
 '09_greenhouse_detail':((-4,14,23),(7.1,1.6,6.9),13),
}
selected=sys.argv[1:] or list(views)
for name in selected:
 pos,focus,scale=views[name];cam.SetPosition(*pos);cam.SetFocalPoint(*focus);cam.SetViewUp(0,1,0 if name!='03_top' else -1)
 if name=='03_top':cam.SetViewUp(0,0,-1)
 cam.SetParallelScale(scale*.54)
 ren.ResetCameraClippingRange();win.SetSize(1400 if name in ['01_hero','02_overview','03_top'] else 1150,940 if name in ['01_hero','02_overview','03_top'] else 770)
 win.Render()
 f=vtk.vtkWindowToImageFilter();f.SetInput(win);f.ReadFrontBufferOff();f.Update();w=vtk.vtkPNGWriter();w.SetFileName(os.path.join(OUT,f'{name}.png'));w.SetInputConnection(f.GetOutputPort());w.Write();print(name,os.path.getsize(os.path.join(OUT,f'{name}.png')),flush=True)
