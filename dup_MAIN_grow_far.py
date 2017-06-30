import rhinoscriptsyntax as rs
import scriptcontext
import operator 
import math
import random
import time
import Rhino
import Nirvik_UI_Utility

from parcel_class_file_new import Parcel_class
from cell_class_file import Cell_class

# cell = m,m,m  # coefficient= k_cell
# parcel=4m,m,m 
# block=16m,8m,m
# avenue=4m,8m,0 x 2
# street=2m,m,0 x 3
rs.ClearCommandHistory()
########################################
####            FUNCTIONS           ####
########################################
def genGeo(sender, e):
    rs.EnableRedraw(False)
    print("building geometry...")
    NUM_BLOCKS_X=int(ui_NUM_BLOCKS_X.Value)
    NUM_BLOCKS_Y=int(ui_NUM_BLOCKS_Y.Value)
    DIM_A=int((BLOCK_LENGTH*(NUM_BLOCKS_X+1) + AVENUE_WIDTH*(NUM_BLOCKS_X+2)))     #length of canvas
    DIM_B=int((BLOCK_WIDTH*(NUM_BLOCKS_Y+1) + STREET_WIDTH*(NUM_BLOCKS_Y+2)))      #breadth of canvas

    # plot avenue
    print("plotting avenue...")
    for i in range(0,(DIM_A+BLOCK_WIDTH+AVENUE_WIDTH),(BLOCK_LENGTH+AVENUE_WIDTH)):
        p0=[]
        p0.append([i,0,0])
        p0.append([i+AVENUE_WIDTH,0,0])
        p0.append([i+AVENUE_WIDTH,DIM_B,0])
        p0.append([i,DIM_B,0])
        p0.append([i,0,0])
        p0_f=rs.AddPolyline(p0)
        rs.ObjectLayer(p0_f,"_prog_avenue")
        AVENUE_LIST.append(p0_f)
    
    # plot street
    print("plotting streets...")
    for i in range(AVENUE_WIDTH,DIM_A,(BLOCK_LENGTH+AVENUE_WIDTH)):
        for j in range(0,DIM_B,(BLOCK_WIDTH+STREET_WIDTH)):
            p0=[]
            p0.append([i,j,0])
            p0.append([i+BLOCK_LENGTH,j,0])
            p0.append([i+BLOCK_LENGTH,j+STREET_WIDTH,0])
            p0.append([i,j+STREET_WIDTH,0])
            p0.append([i,j,0])
            p0_f=rs.AddPolyline(p0)
            rs.ObjectLayer(p0_f,"_prog_street")        
            STREET_LIST.append(p0_f)
    
    # plot blocks
    print("plotting blocks...")
    for i in range(AVENUE_WIDTH,DIM_A,(BLOCK_LENGTH+AVENUE_WIDTH)):
        for j in range(STREET_WIDTH, DIM_B, (BLOCK_WIDTH+STREET_WIDTH)):
            p0=[]
            p0.append([i,j,0])
            p0.append([i+BLOCK_LENGTH,j,0])
            p0.append([i+BLOCK_LENGTH,j+BLOCK_WIDTH,0])
            p0.append([i,j+BLOCK_WIDTH,0])
            p0.append([i,j,0])
            p0_f=rs.AddPolyline(p0)
            rs.ObjectLayer(p0_f,"_prog_block")
            BLOCK_LIST.append(p0_f)    
    
    #plot parcel
    print("plotting parcels...")
    for i in BLOCK_LIST:
        crv_pts=rs.CurvePoints(i)
        x0=int(crv_pts[0][0])
        y0=int(crv_pts[0][1])
        # plot set 1 and 3 of parcels (outer vertically stacked cells)
        j=0
        k=0
        for j in range( x0, x0 + BLOCK_LENGTH, PARCEL_LENGTH+8*PARCEL_WIDTH):
            for k in range( y0, y0+BLOCK_WIDTH, PARCEL_WIDTH):
                p0=[]
                p0.append([j,k,0])
                p0.append([j+PARCEL_LENGTH,k,0])
                p0.append([j+PARCEL_LENGTH,k+PARCEL_WIDTH,0])
                p0.append([j,k+PARCEL_WIDTH,0])            
                p0.append([j,k,0])
                f_p0=rs.AddPolyline(p0)
                rs.ObjectLayer(f_p0,"_prog_parcel")
                HOR_PARCEL_LIST.append(rs.AddPolyline(p0))
        # plot set 1 and 3 of parcels (inner horizontally stacked cells)
        j=0
        k=0
        for k in range(y0, y0+BLOCK_WIDTH, PARCEL_LENGTH):
            for j in range(x0+PARCEL_LENGTH, x0+BLOCK_LENGTH-PARCEL_LENGTH, PARCEL_WIDTH):
                p0=[]
                p0.append([j,k,0])
                p0.append([j+PARCEL_WIDTH,k,0])
                p0.append([j+PARCEL_WIDTH,k+PARCEL_LENGTH,0])
                p0.append([j,k+PARCEL_LENGTH,0])
                p0.append([j,k,0])
                f_p0=rs.AddPolyline(p0)
                rs.ObjectLayer(f_p0,"_prog_parcel")
                VER_PARCEL_LIST.append(f_p0)
    PARCEL_LIST.append(HOR_PARCEL_LIST)
    PARCEL_LIST.append(VER_PARCEL_LIST)
    rs.EnableRedraw(True)
    initGrowth()

def initGrowth():
    print("initialize growth...")
    ####    CONSTRUCT PARCELS  ####
    rs.EnableRedraw(False)
    CELL_CYCLE=int(ui_CELL_CYCLE.Value)
    FAR_TIME_CYCLE=int(ui_FAR_TIME_CYCLE.Value)
    FAR_INC=int(ui_FAR_INC.Value)
    k=0
    for i in PARCEL_LIST[0]:
        crv_pts=rs.CurvePoints(i)
        x0=crv_pts[0][0]
        y0=crv_pts[0][1]
        ax=crv_pts[1][0]-crv_pts[0][0]
        by=crv_pts[2][1]-crv_pts[1][1]
        PARCEL_CLASS_LIST.append(Parcel_class(x0,y0,ax,by,CELL_CYCLE,FAR_TIME_CYCLE,FAR_INC)) ######### PARCEL CLASS INIT
        k+=1
    k1=k
    for i in PARCEL_LIST[1]:
        crv_pts=rs.CurvePoints(i)
        x0=crv_pts[0][0]
        y0=crv_pts[0][1]
        ax=crv_pts[1][0]-crv_pts[0][0]
        by=crv_pts[2][1]-crv_pts[1][1]
        PARCEL_CLASS_LIST.append(Parcel_class(x0,y0,ax,by,CELL_CYCLE,FAR_TIME_CYCLE,FAR_INC)) ######### PARCEL CLASS INIT
        k1+=1
    rs.EnableRedraw(True)
    growInTime()
    pass
 ######### TIME BASED CYCLES DEVELOPMENT

def growInTime():
    rs.EnableRedraw(False)
    MAX_TIME=int(ui_MAXIMUM_TIME.Value)
    VAL_STREET=int(ui_VAL_STREET.Value)
    VAL_AVENUE=int(ui_VAL_AVENUE.Value)
    VAL_STREET_AVENUE=int(ui_VAL_STREET.Value+ui_VAL_AVENUE.Value)
    VAL_DEFAULT=int(ui_VAL_DEFAULT.Value)
    CELL_CYCLE=int(ui_CELL_CYCLE.Value)
    FAR_TIME_CYCLE=int(ui_FAR_TIME_CYCLE.Value)
    FAR_INC=int(ui_FAR_INC.Value)
    IMG_TIME=int(ui_OUTPUT_IMG_TIME.Value)
    #### GLOBAL  MAXIMUM FAR 
    global_far_i=1
    for i in range(1,MAX_TIME,1):
        global_far_i*=(1+(FAR_INC/100))
    GLOBAL_MAX_FAR=global_far_i*(len(PARCEL_CLASS_LIST))
    print("max far="+str(GLOBAL_MAX_FAR))
    print("developing the system in time...")
    
    for i in PARCEL_CLASS_LIST:
        i.buildCells(CELL_LENGTH, CELL_WIDTH)
        i.initCellVal(STREET_LIST, VAL_STREET, AVENUE_LIST, VAL_AVENUE, VAL_DEFAULT)
        i.mapValCellToParcel()
        pass
    LOCAL_FAR=1.0
    for i in range(1,int(MAX_TIME),1):
        LOCAL_FAR*=((1+(FAR_INC/100)))
        print("SYSTEM TIME  : "+ str(i)+" / "+str(MAX_TIME))
        if(scriptcontext.escape_test(False)):
            print("USER PRESSED ESCAPE KEY")
            break
        if(i==int(MAX_TIME/IMG_TIME) and ui_OUT_IMG_YES.Checked==True):
            showAndExportImage()
            pass
        if (ui_RENDER_YES.Checked==True):
            rs.Redraw()
        k=0
        for j in PARCEL_CLASS_LIST: 
            if(k<len(PARCEL_CLASS_LIST)-1):
                A=PARCEL_CLASS_LIST[k]
                B=PARCEL_CLASS_LIST[k+1]
                try:
                    a_root_cen=rs.CurveAreaCentroid(A.root)[0]
                    b_root_cen=rs.CurveAreaCentroid(B.root)[0]
                    d_root=rs.Distance(a_root_cen,b_root_cen)
                    if(d_root<=A.by  or d_root<=A.ax and (A.ax==B.ax and A.by==B.by)):
                        n=random.randrange(1,100)
                        if(n<2 and A.ax<8 and A.by<8):
                            req_l=CELL_LENGTH*4
                            req_b=CELL_WIDTH*4
                            x=A.mergeParcel(B, req_l, req_b)
                            if(x==1):
                                A.delOBJECT_A()
                                A.constructRoot()
                                A.buildCells(CELL_LENGTH, CELL_WIDTH)
                                A.initCellVal(STREET_LIST, VAL_STREET, AVENUE_LIST, VAL_AVENUE, VAL_DEFAULT)
                                for t in range(i):
                                    A.update(t,FAR_TIME_CYCLE, FAR_INC, LOCAL_FAR) ######### UPDATE MERGER TO CURRENT VALUE
                                A.mapValCellToParcel()
                                B.delOBJECT_B()
                                del(PARCEL_CLASS_LIST[k+1])
                                print("merge complete")
                            else:
                                #print("AX, BY, X0, Y0 problems")
                                pass
                        else:
                            #print("Already too BIG")
                            pass
                    else:
                        #print("too far away - D_ROOT to CEN")
                        pass
                except:
                    pass
            PARCEL_CLASS_LIST[k].update(i,FAR_TIME_CYCLE, FAR_INC, LOCAL_FAR)  ######### UPDATE PARCEL CLASS
            k+=1
        pass
    FIND_FAR_REACHED=0
    for i in PARCEL_CLASS_LIST:
        try:
            i.completePARCEL()
        except:
            pass
        FIND_FAR_REACHED+=i.CURR_FAR
    print("final FAR reached="+str(FIND_FAR_REACHED))
    rs.EnableRedraw(True)

def showAndExportImage():    
    rs.Redraw()                
    K=ms=time.time()
    string_img=str("test"+str(K)+".jpg")
    img=rs.CreatePreviewImage(string_img)
    print("img created")

########################################
####            FUNCTIONS           ####
########################################


##################################################
####        GLOBAL DIMENSION VARIABLES        ####
##################################################
render_background_color=1
rs.RenderColor(render_background_color, (255,255,255))
CELL_LENGTH=1
CELL_WIDTH=1 
CELL_LIST=[]
CELL_FAR_LIST=[]
CELL_CYCLE=10 #####     MAX TIME FOR CELL TO GROW
COLOR_LIST=[]
#NUM_BLOCKS_X=2   #default 2
#NUM_BLOCKS_Y=4   #default 4
rs.AddLayer("_prog_cell")
rs.AddLayer("_prog_init_cell_val")

PARCEL_CLASS_LIST=[]
PARCEL_LENGTH=4*CELL_LENGTH
PARCEL_WIDTH=1*CELL_WIDTH
HOR_PARCEL_LIST=[]
VER_PARCEL_LIST=[]
PARCEL_LIST=[]
rs.AddLayer("_prog_parcel")

BLOCK_LENGTH=2*PARCEL_LENGTH+8*PARCEL_WIDTH
BLOCK_WIDTH=8*PARCEL_WIDTH
BLOCK_LIST=[]
rs.AddLayer("_prog_block")

AVENUE_WIDTH=4*CELL_LENGTH
STREET_WIDTH=2*CELL_WIDTH
AVENUE_LIST=[]
STREET_LIST=[]
rs.AddLayer("_prog_avenue")
rs.AddLayer("_prog_street")
"""
DIM_A=(BLOCK_LENGTH*(NUM_BLOCKS_X+1) + AVENUE_WIDTH*(NUM_BLOCKS_X+2))      #length of canvas
DIM_B=(BLOCK_WIDTH*(NUM_BLOCKS_Y+1) + STREET_WIDTH*(NUM_BLOCKS_Y+2))       #breadth of canvas
"""
rs.AddLayer("_prog_3d_geo")
##################################################
####        GLOBAL DIMENSION VARIABLES        ####
##################################################


#############################################
####        GLOBAL CITY VARIABLES        ####
#############################################
#FAR_TIME_CYCLE=10.0     #   FAR INCREMENTS EVERY N TEARS
#FAR_INC=10.0            #   INCREMENT IN FAR EVERY FAR_TIME_CYCLE
#VAL_STREET=0.25         #   default 0.25
#VAL_AVENUE=0.50         #   default 0.50
#VAL_STREET_AVENUE=0.75  #   default 0.75
#VAL_DEFAULT=0.10
FLOOR_HT=1.0
####    TIME BASED ITERATION    ####
CURR_TIME=0
CURR_FAR=1
####    LIMITS of ITERATIVE CYCLES  ####
#MAX_TIME=20.0
#############################################
####        GLOBAL CITY VARIABLES        ####
#############################################


########################################
####         FUNCTION CALLS         ####
########################################
"""
genGeo()
initGrowth()
growInTime()
"""
########################################
####         FUNCTION CALLS         ####
########################################


##############################################
####         USER INTERFACE CALLS         ####
##############################################

ui=Nirvik_UI_Utility.UIForm("FAR BASED GROWTH SIMULATOR")
ui.panel.addLabel("", "", None, True)


ui.panel.addLabel("", "Cell Time Cycle", (0,0,0), False)
ui.panel.addLabel("", "min=25  max=100  default=30",(150,100,100), True)
ui_CELL_CYCLE=ui.panel.addTrackBar("", 1,100,5,10,10,30,500,True, None)

ui.panel.addLabel("", "F.A.R. Time Cycle", (0,0,0), False)
ui.panel.addLabel("", "min=25  max=100  default=40",(150,100,100), True)
ui_FAR_TIME_CYCLE=ui.panel.addTrackBar("", 1,100,5,10,10,40,500,True, None)

ui.panel.addLabel("", "F.A.R. Increment % on each cycle", (0,0,0), False)
ui.panel.addLabel("", "min=1.0%  max=20.0%  default=5%",(150,100,100), True)
ui_FAR_INC=ui.panel.addTrackBar("", 1,20,1,4,2,5,500,True, None)


ui.panel.addLabel("", "Value of Cell next to Street",(0,0,0), False)
ui.panel.addLabel("", "min=0.10 max=1.00 default=0.25",(150,100,100), True)
ui_VAL_STREET=ui.panel.addTrackBar("", 1,100,10,5,10,25,500,True, None)# div by 100


ui.panel.addLabel("", "Value of Cell next to Avenue",(0,0,0), False)
ui.panel.addLabel("", "min=0.01 max=1.00 default=0.75", (150,100,100), True)
ui_VAL_AVENUE=ui.panel.addTrackBar("", 1,100,5,10,10,75,500,True, None)# div by 100


ui.panel.addLabel("", "Default Value of each Cell",(0,0,0), False)
ui.panel.addLabel("", "min=0.01 max=1.00 default=0.10", (150,100,100), True)
ui_VAL_DEFAULT=ui.panel.addTrackBar("", 1,100,5,10,10,10,500,True, None)# div by 100


ui.panel.addLabel("", "Maximum Time", (0,0,0), False)
ui.panel.addLabel("", "min=5  max=500  default=50",(150,100,100), True)
ui_MAXIMUM_TIME=ui.panel.addTrackBar("", 1,500,10,50,25,50,500,True, None)


ui.panel.addLabel("", "Number of Blocks on X Axis", (0,0,0), False)
ui.panel.addLabel("", "min=1  max=4  default=2",(150,100,100), True)
ui_NUM_BLOCKS_X=ui.panel.addTrackBar("", 0,4,2,1,1,1,500,True, None)#add 1


ui.panel.addLabel("", "Number of Blocks on Y-Axis", (0,0,0), False)
ui.panel.addLabel("", "min=1  max=4  default=2",(150,100,100), True)
ui_NUM_BLOCKS_Y=ui.panel.addTrackBar("", 0,4,2,1,1,1,500,True, None)#add 1


ui.panel.addLabel("", "OUTPUT VARIABLES", (0,0,255), True)
ui.panel.addLabel("", "", None, True)
ui.panel.addLabel("", "Output Images ?", (0,0,0), False)
ui_OUT_IMG_YES=ui.panel.addCheckBox("", "YES", False, False, None)
ui.panel.addSeparator("",100,False)
ui.panel.addLabel("", "Show development ?", (0,0,0), False)
ui_RENDER_YES=ui.panel.addCheckBox("", "YES", False, True, None)

ui.panel.addLabel("", "Output for each Iteration in Time", (0,0,0), False)
ui.panel.addLabel("", "min=5  max=100  default=10",(150,100,100), True)
ui_OUTPUT_IMG_TIME=ui.panel.addTrackBar("", 1,100,25,50,25,10,500,True, None)

ui.panel.addButton("", "MAKE DRAWING", 520,True, genGeo)

ui.panel.addLabel("", "", None, True)
ui.panel.addSeparator("",210,False)
ui.panel.addLabel("", "THANK YOU", (0,70,0), False)
ui.panel.addSeparator("",350,True)
ui.panel.addLabel("", "", None, True)



ui.layoutControls()
Rhino.UI.Dialogs.ShowSemiModal(ui)
