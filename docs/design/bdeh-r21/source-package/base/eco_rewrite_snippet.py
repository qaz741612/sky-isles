def build_E2(s):
  """R21 replacement for E: continuous sculptural *ascending* inhabited roof landscape.
  A terraced eco-civic building, not a greenhouse and not two stacked rectangular roof sheets.
  """
  from math import pi,sin
  lower=[(-5.85,2.45),(6.35,1.7),(10.9,3.55),(11.85,8.55),(5.8,11.15),(-3.75,9.8),(-7.65,6.1)]
  poly(s,'EcologicalCivicAtriumPodium',lower,.2,.6,'stone2')
  # Two actual inhabitable levels, shared light court and resilient service wing
  mid=[(-4.25,3.25),(7.85,2.85),(9.85,6.95),(5.9,10.15),(-4.45,8.65)]
  poly(s,'ClimateCommunityFirstFloor',mid,.65,.9,'ivory')
  poly(s,'ClimateCommunityMezzanine',mid,3.54,3.9,'sand')
  # Real glass shell, timber columns, and living wall
  for i,(a,b) in enumerate(zip(mid,mid[1:]+mid[:1])):
    glass(s,'ContinuousOpenEnvironmentalGallery',a,b,1.0,6.1,max(6,int(np.linalg.norm(np.array(a)-np.array(b))/.72)),'mistglass','copperdark')
    # window spandrel clarifies two floors
    s.panel('ClimateGalleryFloorBand',a,b,3.42,3.75,'warmwood',.21)
  # bookend open outdoor ecology pavilion, attached to atrium side, no extra tall tower
  for x,z in [(-6.7,3.45),(-6.7,6.2),(-3.4,3.45),(-3.4,6.2)]:
    post(s,'EcologyClimatePublicVerandaBearing',x,z,.24,4.1,.125,'warmwood')
  poly(s,'IntegratedEcoVerandaRoof',[(-7.5,2.8),(-2.8,2.75),(-2.8,7),(-7.5,7)],4.1,4.40,'ochre')
  # The sweeping landform includes a single low-edge-to-high-edge roof, divided by
  # a luminous skylight strip; both sides share grade, cantilevers and occupied base.
  def living(x,z):
     a=(x+7.5)/20.1;b=(z-.6)/11.1
     y=1.45+2.3*a+4.45*b+0.75*sin(pi*a)*sin(pi*b)
     return [x,y,z]
  # solar shell with expressive wave geometry, not a stack of slabs
  s.surface('MainLivingLandformWest',-7.5,2.25,.8,10.0,living,'sage',32,24,.54)
  s.surface('MainLivingLandformEast',3.55,12.6,.8,10.0,living,'lichen',31,24,.54)
  # long polycarbonate roof lightwell runs *between* both green wings
  def skyl(x,z):
      a=(x+7.5)/20.1;b=(z-.6)/11.1
      return [x,1.5+2.3*a+4.45*b+.75*sin(pi*a)*sin(pi*b)+.12,z]
  s.surface('RainwaterSkyLight',2.20,3.58,.8,10.0,skyl,'mistglass',6,28,.22)
  # dramatic timber/steel load path from roof into occupied column grid
  for x in np.linspace(-6.55,11.55,17):
    for z in (3.05,7.9):
      y=living(x,z)[1]
      if y>1.7:
        post(s,'EcologyEarthRoofStructure',x,z,.22,y-.18,.105,'warmwood')
        beam(s,'EcologyCrossBracedWoodStructure',(x,.24,z),(x+.7,y-.28,z-.55),.065,'copperdark')
  # real shallow landscape terraces as extensions of the ascending roof
  for k,z in enumerate(np.linspace(4.0,8.55,7)):
      for x in np.linspace(-5.8,11.0,15):
          if (round(x*2)+k)%4==0:
              y=living(x,z)[1]
              box(s,'VegetatedRoofNativeGroundcover',x,z,.58,.30,y+.02,y+.19,'darkolive' if k%2 else 'leaf')
  # Living moss-green stepped parapet leads from public garden to landmark roof
  for x,z in [(-6.2,3.4),(-5.7,4.45),(-5.2,5.5),(-4.6,6.6)]:
      y=living(x,z)[1]
      box(s,'LivingGreenRoofEntrySteps',x,z,1.0,.60,.25,max(.54,y-.22),'stone2')
  # integrated environmental canal, not a second dam / old flat thin stripe
  water=[(-5.9,-.45),(-2.8,-.7),(.2,-1.55),(3.2,-2.4),(6.4,-2.15),(9.5,-1.45),(8.8,-.55),(5.6,-1.28),(2.2,-1.5),(-.85,-.55),(-4.25,.2)]
  poly(s,'SinuousRainGardenStoneBank',water,.14,.31,'stone2')
  poly(s,'SinuousRainGardenWater',[(x*.98,z*.97) for x,z in water],.32,.365,'aqua')
  for x,z in [(-8.7,8.1),(-7.4,11.25),(10.9,11.8)]:
     if s._publicCorridor.distance(Point(x,z))>3:s.tree(x,z,.6,'olive')
