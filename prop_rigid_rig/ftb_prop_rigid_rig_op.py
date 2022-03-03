import bpy
from bpy.types import Operator
from math import radians


class FTB_OT_SetRootFromCursor(Operator):
    bl_idname = "object.set_root_from_cursor"
    bl_label = "Root from Cursor"
    bl_description = "Set root bone position from 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.window_manager.ftbRootLoc = bpy.context.scene.cursor.location
        return {'FINISHED'}


class FTB_OT_SetHandleFromCursor(Operator):
    bl_idname = "object.set_handle_from_cursor"
    bl_label = "Handle from Cursor"
    bl_description = "Set handle bone position from 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.window_manager.ftbHandleLoc = bpy.context.scene.cursor.location
        return {'FINISHED'}


class FTB_OT_CreateRigidRig_Op(Operator):
    bl_idname = "object.create_rigid_rig"
    bl_label = "Create Rig"
    bl_description = "Create a simple rig for rigid assets"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj:
            return True

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        childObjs = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        handleLoc = bpy.context.window_manager.ftbHandleLoc
        rootLoc = bpy.context.window_manager.ftbRootLoc

        # set up Armature Object and relevant data
        propRigData = bpy.data.armatures.new(bpy.context.window_manager.ftbPropRigName)
        edit_bones = propRigData.edit_bones
        propRigObj = bpy.data.objects.new(bpy.context.window_manager.ftbPropRigName, propRigData)
        bpy.context.scene.collection.objects.link(propRigObj)

        # switch to edit mode so that editing edit_bones becomes possible
        bpy.context.view_layer.objects.active = propRigObj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        rootBone = edit_bones.new(name="root")
        rootBone.head = rootLoc
        rootBone.tail = (rootLoc[0], rootLoc[1], rootLoc[2] + 1)

        handleBone = edit_bones.new(name="handle")
        handleBone.head = handleLoc
        handleBone.tail = (handleLoc[0], handleLoc[1], handleLoc[2] + 1)

        handleBone.parent = rootBone

        # switch to object mode to finalize changes to edit_bones
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # create root widget
        rootMeshObj = bpy.data.objects.new(("WGT-" +
                                            bpy.context.window_manager.ftbPropRigName + "_root"), createRootMesh())
        bpy.context.scene.collection.objects.link(rootMeshObj)

        # create handle widget

        handleMeshObj = bpy.data.objects.new(
            ("WGT-" + bpy.context.window_manager.ftbPropRigName + "_handle"), createCubeMesh(1))
        bpy.context.scene.collection.objects.link(handleMeshObj)

        handleMeshObj.hide_render = True
        rootMeshObj.hide_render = True

        handleMeshObj.hide_viewport = True
        rootMeshObj.hide_viewport = True

        # rotate custom bone shape rotation

        propRigObj.pose.bones['root'].custom_shape_rotation_euler[0] = radians(-90)
        propRigObj.pose.bones['handle'].custom_shape_rotation_euler[0] = radians(-90)

        # set custom shapes to bones

        propRigObj.pose.bones['root'].custom_shape = rootMeshObj
        propRigObj.pose.bones['handle'].custom_shape = handleMeshObj

        if childObjs:
            for obj in childObjs:
                obj.select_set(True)

            propRigObj.select_set(True)
            bpy.context.view_layer.objects.active = propRigObj
            # set active bone to handleBone to prepare for parenting
            propRigData.bones.active = propRigData.bones['handle']
            propRigData.bones['handle'].select = True

            bpy.ops.object.parent_set(type='BONE')

        return {'FINISHED'}


def createRootMesh():
    verts = [(0.7071067690849304, 0.7071067690849304, 0.0), (0.7071067690849304, -0.7071067690849304, 0.0), (-0.7071067690849304, 0.7071067690849304, 0.0), (-0.7071067690849304, -0.7071067690849304, 0.0), (0.8314696550369263, 0.5555701851844788, 0.0), (0.8314696550369263, -0.5555701851844788, 0.0), (-0.8314696550369263, 0.5555701851844788, 0.0), (-0.8314696550369263, -0.5555701851844788, 0.0), (0.9238795042037964, 0.3826834261417389, 0.0), (0.9238795042037964, -0.3826834261417389, 0.0), (-0.9238795042037964, 0.3826834261417389, 0.0), (-0.9238795042037964, -0.3826834261417389, 0.0), (0.9807852506637573, 0.19509035348892212, 0.0), (0.9807852506637573, -0.19509035348892212, 0.0), (-0.9807852506637573, 0.19509035348892212, 0.0), (-0.9807852506637573, -0.19509035348892212, 0.0), (0.19509197771549225, 0.9807849526405334, 0.0), (0.19509197771549225, -0.9807849526405334, 0.0), (-0.19509197771549225, 0.9807849526405334, 0.0), (-0.19509197771549225, -0.9807849526405334, 0.0), (0.3826850652694702, 0.9238788485527039, 0.0), (0.3826850652694702, -0.9238788485527039, 0.0), (-0.3826850652694702, 0.9238788485527039, 0.0),
             (-0.3826850652694702, -0.9238788485527039, 0.0), (0.5555717945098877, 0.8314685821533203, 0.0), (0.5555717945098877, -0.8314685821533203, 0.0), (-0.5555717945098877, 0.8314685821533203, 0.0), (-0.5555717945098877, -0.8314685821533203, 0.0), (0.19509197771549225, 1.2807848453521729, 0.0), (0.19509197771549225, -1.2807848453521729, 0.0), (-0.19509197771549225, 1.2807848453521729, 0.0), (-0.19509197771549225, -1.2807848453521729, 0.0), (1.280785322189331, 0.19509035348892212, 0.0), (1.280785322189331, -0.19509035348892212, 0.0), (-1.280785322189331, 0.19509035348892212, 0.0), (-1.280785322189331, -0.19509035348892212, 0.0), (0.3950919806957245, 1.2807848453521729, 0.0), (0.3950919806957245, -1.2807848453521729, 0.0), (-0.3950919806957245, 1.2807848453521729, 0.0), (-0.3950919806957245, -1.2807848453521729, 0.0), (1.280785322189331, 0.39509034156799316, 0.0), (1.280785322189331, -0.39509034156799316, 0.0), (-1.280785322189331, 0.39509034156799316, 0.0), (-1.280785322189331, -0.39509034156799316, 0.0), (0.0, 1.5807849168777466, 0.0), (0.0, -1.5807849168777466, 0.0), (1.5807852745056152, 0.0, 0.0), (-1.5807852745056152, 0.0, 0.0)]
    edges = [(0, 4), (1, 5), (2, 6), (3, 7), (4, 8), (5, 9), (6, 10), (7, 11), (8, 12), (9, 13), (10, 14), (11, 15), (16, 20), (17, 21), (18, 22), (19, 23), (20, 24), (21, 25), (22, 26), (23, 27), (0, 24), (1, 25), (2, 26), (3, 27), (16, 28),
             (17, 29), (18, 30), (19, 31), (12, 32), (13, 33), (14, 34), (15, 35), (28, 36), (29, 37), (30, 38), (31, 39), (32, 40), (33, 41), (34, 42), (35, 43), (36, 44), (37, 45), (38, 44), (39, 45), (40, 46), (41, 46), (42, 47), (43, 47)]
    mesh = bpy.data.meshes.new((bpy.context.window_manager.ftbPropRigName + '_root'))
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    return mesh


def createCubeMesh(radius):
    r = radius
    verts = [(r, r, r), (r, -r, r), (-r, -r, r), (-r, r, r),
             (r, r, -r), (r, -r, -r), (-r, -r, -r), (-r, r, -r)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
             (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    mesh = bpy.data.meshes.new((bpy.context.window_manager.ftbPropRigName + '_handle'))
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    return mesh


def create_diamond_widget(radius=0.5):
    """Creates a basic octahedron widget"""
    r = radius
    verts = [(r, 0, 0), (0, -r, 0), (0, r, 0), (0, 0, -r), (0, 0, r), (-r, 0, 0)]
    edges = [(0, 1), (2, 3), (4, 5), (1, 5), (5, 2), (0, 2),
             (4, 2), (3, 1), (1, 4), (5, 3), (3, 0), (4, 0)]
    mesh = bpy.data.meshes.new((bpy.context.window_manager.ftbPropRigName + '_handle'))
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    return mesh


def register():
    bpy.utils.register_class(FTB_OT_CreateRigidRig_Op)
    bpy.utils.register_class(FTB_OT_SetRootFromCursor)
    bpy.utils.register_class(FTB_OT_SetHandleFromCursor)


def unregister():
    bpy.utils.unregister_class(FTB_OT_SetHandleFromCursor)
    bpy.utils.unregister_class(FTB_OT_SetRootFromCursor)
    bpy.utils.unregister_class(FTB_OT_CreateRigidRig_Op)
