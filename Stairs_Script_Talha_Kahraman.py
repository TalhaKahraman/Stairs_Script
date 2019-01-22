from functools import partial

class Make_stairs():
    def __init__(self):
        self.buildUI()
    
    def buildUI(self):
        self.window = cmds.window( title='Stair Generator', widthHeight=(200, 100) )
        cmds.columnLayout( adjustableColumn=True )
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=[100, 200])
        cmds.text(label='Name')
        self.name_textfield = cmds.textField()
        cmds.setParent('..')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=[100, 200])
        cmds.text(label='Number Of Steps')
        self.steps_intfield = cmds.intField(value=10, min=1)
        cmds.setParent('..')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=[100, 200])
        cmds.text(label='radius')
        self.radius_floatfield = cmds.floatField(value=1.0)
        cmds.setParent('..')
        
        cmds.button( label='Make Stairs', command=self.on_make_stairs_clicked)
        cmds.setParent( '..' )
        
    def show(self):
        cmds.showWindow( self.window )
        
    def increment_name(self, name):
        name_list = name.split("_")
        num = name_list[1]
        num = int(num)
        num = num + 1
        num = str(num)
        name_str = "_".join([name_list[0], num, name_list[2]])
        return name_str

    def move_vertices(self, original_step, new_step, step_height):
        desired_top_vtx_pos = cmds.xform(new_step + '.vtx[7]', query=True, translation=True, worldSpace=True)
        # top edge
        cmds.xform(original_step + '.vtx[3]', translation=desired_top_vtx_pos, worldSpace=True)
        # bottom edge
        desired_bot_vtx_pos = [desired_top_vtx_pos[0], desired_top_vtx_pos[1]-step_height, desired_top_vtx_pos[2]]
        cmds.xform(original_step + '.vtx[1]', translation=desired_bot_vtx_pos, worldSpace=True)
    
    def make_stairs(self, stairs_name, steps_value, radius_value):
        cmds.undoInfo( openChunk=True )
        if radius_value < 0:
            radius = radius_value * -1.0
        else:
            radius = radius_value

        step_height = 0.6
        step_name = "step_0_geo" 
        cmds.polyCube(width=3, height=step_height, depth=1.25, name=step_name)
        
        cmds.polyMoveVertex(step_name + '.vtx[3]', t=(0.158295, 0, -0.297229))
        cmds.polyMoveVertex(step_name + '.vtx[1]', t=(0.158295, 0, -0.297229))
        cmds.polyMoveVertex(step_name + '.vtx[4]', step_name + '.vtx[6]', tz=(0.319717))
        cmds.move(-1.5, -0.3, -0.305283, step_name + ".scalePivot", step_name + ".rotatePivot")
        cmds.rotate(0.0, radius * -14.0, 0.0, step_name, relative=True)
        cmds.select(clear=True)
        
        step_list = [step_name]
        
        for index in range(steps_value):
            new_objs = cmds.duplicate(step_name)
            new_name = self.increment_name(step_name)
            cmds.rename(new_objs[0], new_name)
            cmds.parent(new_name, step_name)
                
            # move newly created objects
            cmds.move(0, step_height, 0.931,  new_name, relative=True, localSpace=True)
            # rotate newly created objects, default rotaion is -14.0 for Y
            cmds.rotate(0.0, radius * -14.0, 0.0,  new_name, relative=True)
            self.move_vertices(step_name,new_name,step_height)
            step_name = new_name
            step_list.append(step_name)
            
        cmds.delete(step_list[-1])
        step_list.remove(step_list[-1])
        cmds.select(step_list, add=True)
        if len(step_list) > 1:
            stairs_name = cmds.polyUnite(name=stairs_name, constructionHistory=False)[0]
            cmds.polyMergeVertex(stairs_name, mergeToComponents=True)
        else:
            cmds.rename(step_list[0], stairs_name)
        
        if radius_value < 0:
            cmds.scale(-1.0, stairs_name, scaleX=True)

        cmds.addAttr(stairs_name, longName = 'stair_radius', keyable=True)
        #change datatype to integer
        cmds.addAttr(stairs_name, longName = 'steps', attributeType = 'long', keyable=True)
        
        cmds.setAttr(stairs_name + '.stair_radius',radius_value)
        cmds.setAttr(stairs_name + '.steps',steps_value)
        cmds.undoInfo( closeChunk=True )
        
        cmds.scriptJob(attributeChange=[stairs_name + '.stair_radius', partial(self.update_stairs, stairs_name)] )
        cmds.scriptJob(attributeChange=[stairs_name + '.steps', partial(self.update_stairs, stairs_name)] )
        
    def update_stairs(self, stairs_name):

        stairs_radius = cmds.getAttr(stairs_name + '.stair_radius')
        steps_value = cmds.getAttr(stairs_name + '.steps')
        cmds.delete(stairs_name)        
        self.make_stairs(stairs_name, steps_value, stairs_radius)

    def on_make_stairs_clicked(self, *args):
        stairs_name = cmds.textField(self.name_textfield, query=True, text=True)
        steps_value = cmds.intField(self.steps_intfield, query=True, value=True)
        radius_value = cmds.floatField(self.radius_floatfield, query=True, value=True)
        
        if steps_value >= 1:
            self.make_stairs(stairs_name, steps_value, radius_value)
        else:
            cmds.confirmDialog( title='Warning', message="Can't accept values less than 1!")
                   
my_ui = Make_stairs()
my_ui.show()