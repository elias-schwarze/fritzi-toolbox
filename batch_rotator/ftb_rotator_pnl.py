import bpy
from bpy.types import Panel

class FTB_PT_Rotator_Panel(Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_label = "Batch Rotator" 
        bl_category = "FTB"
        bl_options = {"DEFAULT_CLOSED"}
        
        #create all needed properties and store in WindowManager
        bpy.types.WindowManager.fMinRotation = bpy.props.FloatProperty(description="Minimum amount to rotate objects by", min=-359, max=359)
        bpy.types.WindowManager.fMaxRotation = bpy.props.FloatProperty(description="Maximum amount to rotate objects by", min=-359, max=359)

        bpy.types.WindowManager.bAxisToggleX = bpy.props.BoolProperty()
        bpy.types.WindowManager.bAxisToggleY = bpy.props.BoolProperty()
        bpy.types.WindowManager.bAxisToggleZ = bpy.props.BoolProperty()

        bpy.types.WindowManager.bRandomizeDirection = bpy.props.BoolProperty(description="Randomize direction in which objects are rotated. (If disabled, always rotate objects according to sign +/-)")

        def draw(self, context):
            layout = self.layout

            #button randomize rotation
            col = layout.column()
            col.scale_y = 1.5
            
            col.operator("object.random_rotation") 

            #min max input boxes
            row = layout.row(align=True)
            row.prop(context.window_manager, "fMinRotation", text="Min:")
            row.prop(context.window_manager, "fMaxRotation", text= "Max:")

            col = layout.column()
            col.prop(context.window_manager, "bRandomizeDirection", text= "Randomize Direction", )
            col = layout.column()
            
            #Axis toggles
            row = layout.row(align=True)
            row.label(text="Axis:")
            row.prop(context.window_manager, "bAxisToggleX", text="X", toggle=True)
            row.prop(context.window_manager, "bAxisToggleY", text="Y", toggle=True)
            row.prop(context.window_manager, "bAxisToggleZ", text="Z", toggle=True)