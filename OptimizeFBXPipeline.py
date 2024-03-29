bl_info = {
    "name": "Optimize FBX",
    "author": "Ken An",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > 优化流程",
    "description": "优化FBX模型,减面、补洞",
    "warning": "",
    "doc_url": "",
    "category": "Pipeline",
}

import bpy
import bmesh

# 创建一个自定义面板类
class CustomPanel(bpy.types.Panel):
    bl_label = "优化模型"  # 面板的名称
    bl_idname = "PT_CustomPanel"  # 面板的唯一标识符
    bl_space_type = 'VIEW_3D'  # 面板所在区域
    bl_region_type = 'UI'  # 面板所在区域的类型
    bl_category = "优化流程"  # 面板所在选项卡的名称

    # 绘制面板内容
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("scene.clear_scene",text = "清空场景")
        layout.operator("scene.import_fbx", text="导入FBX")
        layout.operator("object.delete_loose_element", text="删除游离元素")
        layout.operator("object.dissolve_degenerated", text="融并清理")        
        layout.operator("object.merge_by_distance", text="按间距合并")
        layout.operator("object.fill_holes", text="填补漏洞")
        layout.operator("object.decimate", text="减面")
        layout.operator("scene.export_fbx", text="导出FBX")

# 清空场景
class EmptyScene(bpy.types.Operator):
    bl_idname = "scene.clear_scene"
    bl_label = "清空场景"
    bl_description = "清空整个场景，开始时进行操作"

    def execute(self,context):
        # 获取当前激活对象
        obj = bpy.context.active_object
        # 如果有激活对象
        if obj is not None:
            bpy.ops.object.mode_set(mode='OBJECT')

        if len(bpy.data.objects) > 0:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
        return {'FINISHED'}


# 导入FBX
class ImportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.import_fbx"
    bl_label = "导入FBX场景"
    bl_description = "导入FBX文件"

    def execute(self, context):
        bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 导出FBX
class ExportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.export_fbx"
    bl_label = "导出FBX场景"
    bl_description = "导出FBX文件"

    def execute(self, context):
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 删除游离元素
class DeleteLooseOperator(bpy.types.Operator):
    bl_idname = "object.delete_loose_element"
    bl_label = "删除游离元素"
    bl_description = "删除游离的点、边"

    def execute(self, context):
        meshes = set(o for o in context.selected_objects
                      if o.type == 'MESH')
        for m in meshes:
            bpy.context.view_layer.objects.active = m
            bpy.ops.object.mode_set(mode='OBJECT')  # 确保处于对象模式
            bpy.ops.object.select_all(action='DESELECT')  # 取消所有选择
            m.select_set(True)  # 选择当前对象
            bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式
            bpy.ops.mesh.select_all(action='SELECT')  # 选择所有面
            # 删除游离面
            bpy.ops.mesh.delete_loose(use_faces=True) 
            bpy.ops.object.mode_set(mode='OBJECT')  # 返回对象模式
        return {'FINISHED'}


# 融合面积为零的面以及长度为零的边
class DissolveDegeneratedOperator(bpy.types.Operator):
    bl_idname = "object.dissolve_degenerated"
    bl_label = "融并清理"
    bl_description = "清理面积为零的面以及长度为零的边"

    def execute(self, context):
        # 获取当前选中的对象
        meshes = set(o.data for o in context.selected_objects
                      if o.type == 'MESH')
        bm = bmesh.new()

        for m in meshes:
            bm.from_mesh(m)
            bmesh.ops.dissolve_degenerate(bm, dist=0.0001, edges=bm.edges)
            bm.to_mesh(m)
            m.update()
            bm.clear()

        bm.free()
        return {'FINISHED'}

# 按间距合并
class MergeByDistanceOperator(bpy.types.Operator):
    bl_idname = "object.merge_by_distance"
    bl_label = "按间距合并"
    bl_description = "合并重合的点(按照距离)"

    distance : bpy.props.FloatProperty(name="阈值(m)",default=0.0001)
    
    def execute(self,context):
        d = self.distance        
         # 获取当前选中的对象
        meshes = set(o.data for o in context.selected_objects
                      if o.type == 'MESH')
        bm = bmesh.new()

        for m in meshes:
            bm.from_mesh(m)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=d)
            bm.to_mesh(m)
            m.update()
            bm.clear()

        bm.free()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# 填补漏洞
class FillHoleOperator(bpy.types.Operator):
    bl_idname = "object.fill_holes"
    bl_label = "填补漏洞"
    bl_description = "填补破开的洞"

    sides : bpy.props.IntProperty(name="最大边数",default=20)

    def execute(self,context):
        s = self.sides
        
        # 获取当前选中的对象
        meshes = set(o.data for o in context.selected_objects
                      if o.type == 'MESH')
        bm = bmesh.new()

        for m in meshes:
            bm.from_mesh(m)
            bmesh.ops.holes_fill(bm, edges=bm.edges, sides=s)
            bm.to_mesh(m)
            m.update()
            bm.clear()

        bm.free()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# 定义一个操作符用于添加 "Decimate" 修饰器
class AddDecimateModifierOperator(bpy.types.Operator):
    bl_idname = "object.decimate"
    bl_label = "减面设置"
    bl_description = "给对象添加减面修改器"

    ratio : bpy.props.FloatProperty(name="精简比例",default=0.3)
    
    # 执行操作的函数
    def execute(self, context):
        r = self.ratio
        # 获取当前选中的对象
        meshes = set(o for o in context.selected_objects
                      if o.type == 'MESH')
        for m in meshes:
            bpy.context.view_layer.objects.active = m
            bpy.ops.object.mode_set(mode='OBJECT')  # 确保处于对象模式
            bpy.ops.object.select_all(action='DESELECT')  # 取消所有选择
            m.select_set(True)  # 选择当前对象
            bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式
            bpy.ops.mesh.select_all(action='SELECT')  # 选择所有面

            # 使用Decimate进行减面
            bpy.ops.mesh.decimate(ratio=r)  # 在这里设置减面比率

            bpy.ops.object.mode_set(mode='OBJECT')  # 返回对象模式
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)






# 注册面板和操作符
def register():
    bpy.utils.register_class(CustomPanel)
    bpy.utils.register_class(EmptyScene)
    bpy.utils.register_class(ImportFBXOperator)
    bpy.utils.register_class(ExportFBXOperator)
    bpy.utils.register_class(AddDecimateModifierOperator)
    bpy.utils.register_class(DeleteLooseOperator)
    bpy.utils.register_class(DissolveDegeneratedOperator)
    bpy.utils.register_class(MergeByDistanceOperator)
    bpy.utils.register_class(FillHoleOperator)


# 注销面板和操作符
def unregister():
    bpy.utils.unregister_class(CustomPanel)
    bpy.utils.unregister_class(EmptyScene)
    bpy.utils.unregister_class(ImportFBXOperator)
    bpy.utils.unregister_class(ExportFBXOperator)
    bpy.utils.unregister_class(AddDecimateModifierOperator)
    bpy.utils.unregister_class(DeleteLooseOperator)
    bpy.utils.unregister_class(DissolveDegeneratedOperator)
    bpy.utils.unregister_class(MergeByDistanceOperator)
    bpy.utils.unregister_class(FillHoleOperator)



# 在脚本执行时调用注册函数
if __name__ == "__main__":
    register()
