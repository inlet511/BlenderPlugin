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
class OBJECT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "交互式虚拟模型前处理模块"  # 面板的名称
    bl_idname = "OBJECT_PT_CustomPanel"  # 面板的唯一标识符
    bl_space_type = 'VIEW_3D'  # 面板所在区域
    bl_region_type = 'UI'  # 面板所在区域的类型
    bl_category = "前处理模块"  # 面板所在选项卡的名称

    # 绘制面板内容
    def draw(self, context):
        layout = self.layout
        scene = context.scene        
        
        box = layout.box()
        box.label(text="清理")        
        row1 = box.row()
        row1.operator("scene.clear_scene",text = "清空场景")
        row1.operator("object.delete_loose_element", text="删除游离元素")
        
        row2 = box.row()
        row2.operator("object.dissolve_degenerated", text="融并清理")        
        row2.operator("object.merge_by_distance", text="按间距合并")
        
        box2 = layout.box()
        box2.label(text="补洞")
        
        row3 = box2.row()
        row3.operator("object.select_openedge", text = "高亮破洞")
        row3.operator("object.fill_selected_hole", text = "填充选择的破洞")        
        box2.operator("object.fill_holes", text="自动填补破洞")

        
        box3 = layout.box()
        box3.label(text="减面")
        row4 = box3.row()
        row4.operator("object.decimateselected", text="选择对象减面")
        row4.operator("object.get_vertex_volume_rate", text="获取顶点体积比")
        box3.operator("object.decimate", text="整体减面")
                
        box4 = layout.box()
        box4.label(text="导出")
        box4.operator("scene.export_fbx", text="导出FBX")
        box4.operator("scene.export_obj", text="导出OBJ")

# 清空场景
class OBJECT_OT_EmptyScene(bpy.types.Operator):
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
    
# 选择破洞
class OBJECT_OT_SelectOpenEdgeOperator(bpy.types.Operator):
    bl_idname = "object.select_openedge"
    bl_label = "选择开放边"
    bl_description = "选择开放边"
    
    def execute(self, context):
        # 获取当前选择的对象        
        meshes = set(o for o in context.selected_objects
                      if o.type == 'MESH')

        # 确保对象是网格对象
        for m in meshes:
            bpy.context.view_layer.objects.active = m
            bpy.ops.object.mode_set(mode='OBJECT')  # 确保处于对象模式
            bpy.ops.object.select_all(action='DESELECT')  # 取消所有选择
            m.select_set(True)  # 选择当前对象
            bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式

            # 切换到边模式
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

            # 重置选择
            bpy.ops.mesh.select_all(action='DESELECT')

            # 选中破洞的边
            bpy.ops.mesh.select_non_manifold()
        
        return {'FINISHED'}
    
# 填充选择的破洞
class OBJECT_OT_FillSelectedHoleOperator(bpy.types.Operator):
    bl_idname = "object.fill_selected_hole"
    bl_label = "填充选择的破洞"
    bl_description = "填充选择的破洞"
    
    def execute(self, context):
        # 获取当前活动对象
        obj = bpy.context.active_object
        
        # 确保对象是网格对象
        if obj and obj.type == 'MESH':
            bpy.ops.mesh.loop_multi_select(ring=False)      
            bpy.ops.mesh.fill()  
        
        return {'FINISHED'}

# 导入FBX
class OBJECT_OT_ImportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.import_fbx"
    bl_label = "导入FBX场景"
    bl_description = "导入FBX文件"

    def execute(self, context):
        bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

# 导出FBX
class OBJECT_OT_ExportFBXOperator(bpy.types.Operator):
    bl_idname = "scene.export_fbx"
    bl_label = "导出FBX场景"
    bl_description = "导出FBX文件"

    def execute(self, context):
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}
    
# 导出OBJ
class OBJECT_OT_ExportOBJOperator(bpy.types.Operator):
    bl_idname = "scene.export_obj"
    bl_label = "导出OBJ场景"
    bl_description = "导出OBJ文件"

    def execute(self, context):
        bpy.ops.wm.obj_export('INVOKE_DEFAULT')
        return {'FINISHED'}

# 删除游离元素
class OBJECT_OT_DeleteLooseOperator(bpy.types.Operator):
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
class OBJECT_OT_DissolveDegeneratedOperator(bpy.types.Operator):
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
class OBJECT_OT_MergeByDistanceOperator(bpy.types.Operator):
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
class OBJECT_OT_FillHoleOperator(bpy.types.Operator):
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

# 选中对象减面
class OBJECT_OT_DecimateSelectedOperator(bpy.types.Operator):
    bl_idname = "object.decimateselected"
    bl_label = "减面设置"
    bl_description = "给所选对象减面"
    
    ratio : bpy.props.FloatProperty(name="精简到比例",default=0.3)
    
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


# 获取顶点/体积比
class OBJECT_OT_GetVertexVolumeRateOperator(bpy.types.Operator):
    bl_idname = "object.get_vertex_volume_rate"
    bl_label = "获取顶点体积比"
    bl_description = "获取所选对象的顶点体积比"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    
    message = bpy.props.StringProperty(name="Message", default="")
    
    def execute(self, context):
         # 获取当前选中的对象
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        if len(meshes) == 0:
            self.report({'INFO'}, "请选择一个模型")            
        else:        
            obj = meshes[0]
            vertices_count = len(obj.data.vertices)
            bbox_volume = obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2]
            
            ratio = vertices_count / bbox_volume
            
            self.message = "顶点数: %d, 体积: %f, 顶点体积比: %f" %(vertices_count, bbox_volume, ratio)
            
            self.report({'INFO'},self.message)
        return {'FINISHED'}        


# 定义一个操作符用于添加 Decimate修饰器
class OBJECT_OT_DecimateAll(bpy.types.Operator):
    bl_idname = "object.decimate"
    bl_label = "减面设置"
    bl_description = "给对象添加减面修改器"

    vertex_volume_ratio: bpy.props.FloatProperty(name="顶点体积比", default=5e9)
    ratio : bpy.props.FloatProperty(name="精简到比例",default=0.3)
    
    # 执行操作的函数
    def execute(self, context):
        vvr = self.vertex_volume_ratio
        r = self.ratio
        
        objects = bpy.data.objects
                
        # 遍历所有对象
        for obj in objects:
        # 只考虑是网格的对象
            if obj.type == 'MESH':
                # 获取对象的顶点数和边界框体积
                vertices_count = len(obj.data.vertices)
                bbox_volume = obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2]
                
                # 计算顶点数和bbox体积的比例
                if bbox_volume == 0:
                    self.report({'INFO'}, 'Volume is 0')
                else:
                    vertex_to_bbox_ratio = vertices_count / bbox_volume
                    info_str = str(vertex_to_bbox_ratio)
                    self.report({'INFO'}, info_str)
                    # file.write(info_str + '\n')
                    
                
                    # 如果比例大于阈值，则选择该对象                    
                    if vertex_to_bbox_ratio > vvr:
                        bpy.context.view_layer.objects.active = obj
                        bpy.ops.object.mode_set(mode='OBJECT')  # 确保处于对象模式
                        bpy.ops.object.select_all(action='DESELECT')  # 取消所有选择
                        obj.select_set(True)  # 选择当前对象
                        bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式
                        bpy.ops.mesh.select_all(action='SELECT')  # 选择所有面

                        # 使用Decimate进行减面
                        bpy.ops.mesh.decimate(ratio=r)  # 在这里设置减面比率
                        bpy.ops.object.mode_set(mode='OBJECT')  # 返回对象模式
        # file.close()    
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)






# 注册面板和操作符
def register():
    bpy.utils.register_class(OBJECT_PT_CustomPanel)
    bpy.utils.register_class(OBJECT_OT_EmptyScene)
    bpy.utils.register_class(OBJECT_OT_SelectOpenEdgeOperator)
    bpy.utils.register_class(OBJECT_OT_FillSelectedHoleOperator)
    bpy.utils.register_class(OBJECT_OT_ImportFBXOperator)
    bpy.utils.register_class(OBJECT_OT_ExportFBXOperator)
    bpy.utils.register_class(OBJECT_OT_ExportOBJOperator)
    bpy.utils.register_class(OBJECT_OT_DecimateSelectedOperator)
    bpy.utils.register_class(OBJECT_OT_GetVertexVolumeRateOperator)
    bpy.utils.register_class(OBJECT_OT_DecimateAll)
    bpy.utils.register_class(OBJECT_OT_DeleteLooseOperator)
    bpy.utils.register_class(OBJECT_OT_DissolveDegeneratedOperator)
    bpy.utils.register_class(OBJECT_OT_MergeByDistanceOperator)
    bpy.utils.register_class(OBJECT_OT_FillHoleOperator)


# 注销面板和操作符
def unregister():
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
    bpy.utils.unregister_class(OBJECT_OT_EmptyScene)
    bpy.utils.unregister_class(OBJECT_OT_SelectOpenEdgeOperator)
    bpy.utils.unregister_class(OBJECT_OT_FillSelectedHoleOperator)
    bpy.utils.unregister_class(OBJECT_OT_ImportFBXOperator)
    bpy.utils.unregister_class(OBJECT_OT_ExportFBXOperator)
    bpy.utils.unregister_class(OBJECT_OT_ExportOBJOperator)
    bpy.utils.unregister_class(OBJECT_OT_DecimateSelectedOperator)
    bpy.utils.unregister_class(OBJECT_OT_GetVertexVolumeRateOperator)
    bpy.utils.unregister_class(OBJECT_OT_DecimateAll)
    bpy.utils.unregister_class(OBJECT_OT_DeleteLooseOperator)
    bpy.utils.unregister_class(OBJECT_OT_DissolveDegeneratedOperator)
    bpy.utils.unregister_class(OBJECT_OT_MergeByDistanceOperator)
    bpy.utils.unregister_class(OBJECT_OT_FillHoleOperator)



# 在脚本执行时调用注册函数
if __name__ == "__main__":
    register()
