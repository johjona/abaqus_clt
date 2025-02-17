from abaqus import *
from abaqusConstants import *
from odbAccess import *
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

def createPart(part_name, element_width, element_height, longitudinal_length, transversal_length, orientation, part_names, elements, spatial_width, method):

    partInstances = []


    if orientation == "T":
        
        elements_temp = transversal_length/element_width
        length = transversal_length

    else:

        elements = int(transversal_length/element_width)
        elements_temp = longitudinal_length/element_width
        length = longitudinal_length

    print(elements_temp)

    s = mdb.models[model].ConstrainedSketch(name='__profile__', 
    sheetSize=10.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)

    s.Spot(point=(-element_width/2, -element_height/2))
    s.Spot(point=(-element_width/2, element_height/2))
    s.Spot(point=(element_width/2, element_height/2))
    s.Spot(point=(element_width/2, -element_height/2))

    s.Line(point1=(-element_width/2, -element_height/2), point2=(element_width/2, -element_height/2))
    s.Line(point1=(element_width/2, -element_height/2), point2=(element_width/2, element_height/2))
    s.Line(point1=(element_width/2, element_height/2), point2=(-element_width/2, element_height/2))
    s.Line(point1=(-element_width/2, element_height/2), point2=(-element_width/2, -element_height/2))


    p = mdb.models[model].Part(name=part_name, dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
    p = mdb.models[model].parts[part_name]
    p.BaseSolidExtrude(sketch=s, depth=length + (elements_temp-1)*spatial_width)
    s.unsetPrimaryObject()
    
    a1 = mdb.models[model].rootAssembly

    for k in range(int(elements)):

        part_name = "Part-%s-%s"%(layer_count, k)

                  
        a1.Instance(name='Part-%s'%layer_count + '-%s'%k, part=p, dependent=OFF)
        p1 = a1.instances['Part-%s'%layer_count + '-%s'%k]

         
        spatial_width_temp = spatial_width

        if orientation == "L":
            
            p1.translate(vector=(k*(element_width + spatial_width_temp), y_coord, 0.0))

        if orientation == "T":
     
            p1.translate(vector=(0, y_coord, (element_width+(k)*(element_width + spatial_width_temp)) ))
            a1.rotate(instanceList=(part_name, ), axisPoint=(-(element_width)/2, 10.2, element_width +(k)*(element_width + spatial_width_temp)), 
                 axisDirection=(0.0, element_height, 0.0), angle=90.0)
            
    for k in range(elements):

        partInstances.append(a1.instances["Part-%s-%s"%(layer_count, k)])

    if method == "merge":

        new_part_name = 'Part-%s%s'%(layer_count,layer_count)

        a1.InstanceFromBooleanMerge(name=new_part_name, instances=tuple(partInstances), 
        keepIntersections=ON, originalInstances=SUPPRESS, domain=GEOMETRY)
        part_names.append(new_part_name)

    elif method == "individ":
    
        for k in range(elements):
            part_names.append('Part-%s-%s'%(layer_count, k))

    return part_names 
            
    
def createAndAssignMaterial(part_name, material_name, orientation, elements):

    if orientation == "T":
        rot_angle = 0.0
    else:
        rot_angle = 90.0

    for k in range(elements):

        part_name = part_name

        p = mdb.models[model].parts[part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
        region = p.Set(cells=cells, name='Material-Set-%s'%layer_count)
        p = mdb.models[model].parts[part_name]
        p.SectionAssignment(region=region, sectionName=(material_name + '_section'), offset=0.0, 
            offsetType=MIDDLE_SURFACE, offsetField='', 
            thicknessAssignment=FROM_SECTION)

        p = mdb.models['Model-1'].parts[part_name]
        c = p.cells
        cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
        region = regionToolset.Region(cells=cells)
        mdb.models['Model-1'].parts[part_name].MaterialOrientation(region=region, 
            orientationType=SYSTEM, axis=AXIS_2, localCsys=None, 
            fieldName='', additionalRotationType=ROTATION_ANGLE, 
            additionalRotationField='', angle=rot_angle, stackDirection=STACK_3)
        
  
def createSurfaces(part_name, orientation, y_coord, element_height, element_width, elements, spatial_width):

## -------------- Create top- and bottom surfaces ---------- ##

    all_surfs = []
    all_surfs_bot = []     

    a = mdb.models[model].rootAssembly
    
    for k in range(int(elements)):
        
        if method == "merge":
            merge_name = "-1"
            i = 0
        else:
            merge_name = ""
            i = k

        part_name = part_names[i] + merge_name

        if orientation == "T":
            coord_top = (0.2, y_coord + element_height/2 , 0.1 + k*element_width + (k-1)*spatial_width)
            coord_bot = (0.2, y_coord - element_height/2 , 0.1 + k*element_width + (k-1)*spatial_width)

            s = a.instances[part_name].faces

            sideFaces = s.findAt(((element_width/2, y_coord, element_width + (k)*element_width + k*spatial_width) ,))
            region1=a.Surface(side1Faces=sideFaces, name='side_m_Surf-%s'%(part_name))

            sideFaces = s.findAt(((element_width/2, y_coord, 0 + (k)*element_width + (k)*spatial_width) ,))
            region2=a.Surface(side1Faces=sideFaces, name='side_s_Surf-%s'%(part_name))

        else:
            coord_top = (-0.05 + k*element_width + (k-1)*spatial_width, y_coord + element_height/2,0.95)
            coord_bot = (-0.05 + k*element_width + (k-1)*spatial_width, y_coord - element_height/2,0.95)

            s = a.instances[part_name].faces

            sideFaces = s.findAt(((element_width/2 + (k)*element_width + (k)*spatial_width , y_coord, 2.) ,))
            region1=a.Surface(side1Faces=sideFaces, name='side_m_Surf-%s'%(part_name))

            sideFaces = s.findAt(((-element_width/2 + (k)*element_width + (k)*spatial_width , y_coord, 2.) ,))
            region2=a.Surface(side1Faces=sideFaces, name='side_s_Surf-%s'%(part_name)) 

        # s = a.instances[part_name + "%s-"%layer_count + str(1)].faces
        s = a.instances[part_name].faces
        side1Faces = s.findAt(((coord_top),))
        all_surfs.append(side1Faces)


        # s = a.instances[part_name + "%s-"%layer_count + str(1)].faces
        s = a.instances[part_name].faces
        side1Faces = s.findAt(((coord_bot),))
        all_surfs_bot.append(side1Faces)

    a.Surface(side1Faces=all_surfs, name = 'Top_%s'%layer_count) 
    a.Surface(side1Faces=all_surfs_bot, name = 'Bot_%s'%layer_count) 

def createHorisontalConstraints(part_names, orientation, elements, layer_count):

    a = mdb.models[model].rootAssembly

    for k in range(elements - 1):


        region1 = a.surfaces['side_m_Surf-Part-%s-%s'%(layer_count, k)]
        region2 = a.surfaces['side_s_Surf-Part-%s-%s'%(layer_count, k + 1)]

        mdb.models['Model-1'].Tie(name='Constraint-%s-%s'%(layer_count, k), main=region1, secondary=region2, 
            positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, 
            thickness=ON)
        
    
def createMesh(part_name, seed_size):

## ----------------- Mesh -------------- ##        
    a = mdb.models[model].rootAssembly
    partInstances = []
    
    for k in range(elements):
    
        partInstances.append(a.instances[part_name])
            
    a.seedPartInstance(regions=partInstances, size=seed_size, deviationFactor=0.1, 
    minSizeFactor=0.1)
    
    a.generateMesh(regions=partInstances)
    
    a = mdb.models[model].rootAssembly

    elemType1 = mesh.ElemType(elemCode=C3D20, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=C3D15, elemLibrary=STANDARD)
    elemType3 = mesh.ElemType(elemCode=C3D10, elemLibrary=STANDARD)

    a = mdb.models[model].rootAssembly

    pickedRegions = []
    
    for k in range(elements):
    
        c1 = a.instances[part_name].cells
        cells1 = c1.getSequenceFromMask(mask=('[#1 ]', ), )
        pickedRegions.append(cells1)
    
    a.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
    
    
def createConstrains(LayerDict):

# -------------------- Create constrains ------------------------- #

    a = mdb.models[model].rootAssembly
    
    for i in range(len(LayerDict)):
        
        if i < len(LayerDict)-1:
          
            region1=a.surfaces['Top_%s'%i]
            region2=a.surfaces['Bot_%s'%(i + 1)]
                    
            mdb.models[model].Tie(name='Constraint-%s'%i, main=region1, secondary=region2, 
                positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, 
                thickness=ON)
            
            

   

###############################################################   
###############################################################   
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
### --------------- PRE STUFF STARTS HERE ----------------- ###
### ------------------------------------------------------  ###
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
###############################################################
###############################################################
        
### --------------------- New MDB --------------------------------- ###
 
model = "Model-1"
mdb.Model(name=model, modelType=STANDARD_EXPLICIT)
job_counter = 0  
material_list = ["C14", "C24", "C30", "C40", "C50"]

##---------------------------Material Library---------------------------##

MaterialDict = {}
MaterialDict["C14"]=(7000e6, 230e6, 230e6, 0.48, 0.42, 0.28, 440e6, 440e6, 40e6, 350)
MaterialDict["C24"]=(11000e6, 370e6, 370e6, 0.48, 0.42, 0.28, 690e6, 690e6, 49e6, 420)
MaterialDict["C30"]=(12000e6, 400e6, 400e6, 0.48, 0.42, 0.28, 750e6, 750e6, 49e6, 460)
MaterialDict["C40"]=(14000e6, 470e6, 470e6, 0.48, 0.42, 0.28, 880e6, 880e6, 60e6, 480)
MaterialDict["C50"]=(16000e6, 530e6, 530e6, 0.48, 0.42, 0.28, 1000e6, 1000e6, 70e6, 520)

## ------------------------ Create Materials -------------------------##

for material_name in material_list:

    mdb.models[model].Material(name=material_name)
    mdb.models[model].materials[material_name].Density(table=((MaterialDict[material_name][9], ), ))
    mdb.models[model].materials[material_name].Elastic(type=ENGINEERING_CONSTANTS, table=((MaterialDict[material_name][0], MaterialDict[material_name][1],MaterialDict[material_name][2], MaterialDict[material_name][3],MaterialDict[material_name][4],MaterialDict[material_name][5],MaterialDict[material_name][6],MaterialDict[material_name][7],MaterialDict[material_name][8]), ))
    
    mdb.models[model].HomogeneousSolidSection(name=material_name + '_section', 
    material=material_name, thickness=None)

###############################################################   
###############################################################   
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
### --------------- MAIN CODE STARTS HERE ----------------- ###
### ------------------------------------------------------  ###
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
###############################################################
###############################################################
  
### --------------- Input parameters ----------------- ###

LayerDict = {}
LayerDict["layer0"] = (0.03, "L", "C24")
LayerDict["layer1"] = (0.02, "T", "C14")
LayerDict["layer2"] = (0.02, "L", "C24")
LayerDict["layer3"] = (0.02, "T", "C14")
LayerDict["layer4"] = (0.03, "L", "C24")

spatial_width = 0.0 # gap between lamellas (not working atm
element_width = 0.2 # width of individual lamellas

longitudinal_length_i = 4 # total length of plate - needs to be a multiple of element_width
transversal_length_i = 1 # total width of plate - also needs to be a multiple of element_width

method = "merge" # "merge" or "individ"

###############################################################   
###############################################################   
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
### --------------- MAIN CODE STARTS HERE ----------------- ###
### ------------------------------------------------------  ###
### ------------------------------------------------------- ###
### ------------------------------------------------------- ###
###############################################################
###############################################################

### -------------------- Create model ------------------------------ ###

longitudinal_length = longitudinal_length_i
transversal_length = transversal_length_i 

nbr_of_layers = len(LayerDict)

y_coord = 0

job_name = 'Job-1'

for layer_count in range(len(LayerDict)):

    part_names = []
    
    layer_name = "layer%s"%layer_count

    # --------- Create part for current layer ------------ #
     
    element_height = LayerDict[layer_name][0]
    orientation = LayerDict[layer_name][1]
    material = LayerDict[layer_name][2]
    
    if orientation == "T":
        
        elements = int(longitudinal_length_i/element_width)

    else:

        elements = int(transversal_length_i/element_width)

    part_name = 'Part-%s-'%layer_count

   
    if layer_count != 0:

        y_coord = y_coord + element_height/2

    part_name = 'Part-%s'%(layer_count)

    ## ------------- Part -------------- ##
    
    part_names = createPart(part_name, element_width, element_height, longitudinal_length, transversal_length, orientation, part_names, elements, spatial_width, method)        

    ## ------------- Material -------------- ## 
    
    createAndAssignMaterial(part_name, material_name, orientation, elements)
    
    # ## ------------- Surfaces -------------- ##
    
    createSurfaces(part_names, orientation, y_coord, element_height, element_width, elements, spatial_width)

    if method == "individ":

        createHorisontalConstraints(part_names, orientation, elements, layer_count)
   
    ## ------------- Update coordinate -------------- ##
    
    spatial_height = 0
                       
    y_coord = y_coord + element_height/2 + spatial_height 
    
# -------------- Create Constrains ----------------- ## 

createConstrains(LayerDict)




    








        
