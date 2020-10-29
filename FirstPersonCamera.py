#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 13:51:31 2020

@author: david
"""


from direct.showbase import DirectObject
from panda3d.core import CollisionHandlerPusher, CollisionNode, \
                        CollisionSphere, BitMask32
from panda3d.core import *
from direct.task import Task 

from direct.gui.OnscreenText import OnscreenText

##   First person camera controller, "free view"/"FPS" style.
#    
#    Simple camera mouse look and WASD key controller 
#    shift to go faster,
#    r and f keys move camera up/down, 
#    q and e keys rotate camera,
#    hit enter to start/stop controls.
#    If a refNode is specified, heading and up/down are performed wrt the 
#    reference node (usually the root node of scene, i.e. base.render)
#    and camera behaves more similarly to an "FPS" camera.

class FirstPersonCamera(DirectObject.DirectObject):
    '''
    First person camera controller.
    '''
    
    ## Constructor
    # @param gameaApp: the game application to which this controller
    # applies, that should be ShowBase derived.
    # @param camera: the camera to which this controller applies
    # @param refNode: reference node wrt heading and up/down are performed
    def __init__(self, gameApp, camera, refNode=None,
                 collisionHandler=None):
        '''
        Constructor
        '''
        
        self.gameApp = gameApp
        self.camera = camera
        if refNode != None:
            self.refNode = refNode
        else:
            self.refNode = self.camera
        
    
        self.textObject = OnscreenText(text="", parent = aspect2d, scale=.05,
                            pos=(-0.65, -.65), fg=(1, 1, 1, 1),
                            align=TextNode.ALeft, wordwrap = 15)
        
        self.running = False 
        self.time = 0 
        self.centX = int(self.gameApp.win.getProperties().getXSize() / 2)
        self.centY = int(self.gameApp.win.getProperties().getYSize() / 2)
        
        # key controls 
        self.forward = False 
        self.backward = False 
        self.fast = 1.0 
        self.left = False 
        self.right = False 
        self.up = False 
        self.down = False 
        self.up = False 
        self.down = False 
        self.rollLeft = False 
        self.rollRight = False 
        
        # sensitivity settings 
        self.movSens = 2
        self.movSensFast = self.movSens * 5
        self.rollSens = 50 
        self.sensX = self.sensY = 0.2       
        
        self.collisionHandler = collisionHandler
        self.collideMask = BitMask32(0x10)

        #press enter to get this camera controller
        self.accept("enter", self.toggle)           

    ## Get camera collide mask
    def getCollideMask(self):
        return self.collideMask
    
    ## Camera rotation task 
    def cameraTask(self, task): 
        dt = task.time - self.time 
        
        # handle mouse look 
        md = self.gameApp.win.getPointer(0)        
        x = md.getX() 
        y = md.getY() 
         
        if self.gameApp.win.movePointer(0, self.centX, self.centY):    
            self.camera.setH(self.refNode, self.camera.getH(self.refNode) 
                             - (x - self.centX) * self.sensX) 
            self.camera.setP(self.camera, self.camera.getP(self.camera) 
                             - (y - self.centY) * self.sensY)       
        
        # handle keys: 
        if self.forward == True: 
            self.camera.setY(self.camera, self.camera.getY(self.camera) 
                             + self.movSens * self.fast * dt)
        if self.backward == True:
            self.camera.setY(self.camera, self.camera.getY(self.camera) 
                             - self.movSens * self.fast * dt) 
        if self.left == True:
            self.camera.setX(self.camera, self.camera.getX(self.camera) 
                             - self.movSens * self.fast * dt) 
        if self.right == True:
            self.camera.setX(self.camera, self.camera.getX(self.camera) 
                             + self.movSens * self.fast * dt) 
        if self.up == True:
            self.camera.setZ(self.refNode, self.camera.getZ(self.refNode) 
                             + self.movSens * self.fast * dt) 
        if self.down == True:
            self.camera.setZ(self.refNode, self.camera.getZ(self.refNode) 
                             - self.movSens * self.fast * dt)           
        if self.rollLeft == True:
            self.camera.setR(self.camera, self.camera.getR(self.camera) 
                             - self.rollSens * dt)
        if self.rollRight == True:
            self.camera.setR(self.camera, self.camera.getR(self.camera) 
                             + self.rollSens * dt)
            
        text = str('R = ' + "{:.2f}".format(self.camera.getR())   +
                   '  P = ' + "{:.2f}".format(self.camera.getP()) +
                   '  H = ' + "{:.2f}".format(self.camera.getH()) +
                   '  X = ' + "{:.2f}".format(self.camera.getX()) +
                   '  Y = ' + "{:.2f}".format(self.camera.getY()) +
                   '  Z = ' + "{:.2f}".format(self.camera.getZ()))
        
        self.textObject.setText(text) 

            
        self.time = task.time       
        return Task.cont 

    ## Start to control the camera
    def start(self):
        self.gameApp.disableMouse()
        self.camera.setP(self.refNode, -9.4)
        self.camera.setH(self.refNode, 150)
        self.camera.setR(self.refNode, 0)

        self.camera.setX(self.refNode, +1.6)
        self.camera.setY(self.refNode, +3)
        self.camera.setZ(self.refNode, +1)
        
        # hide mouse cursor, comment these 3 lines to see the cursor 
        props = WindowProperties() 
        props.setCursorHidden(True) 
        self.gameApp.win.requestProperties(props) 
        
        # reset mouse to start position: 
        self.gameApp.win.movePointer(0, self.centX, self.centY)             
        self.gameApp.taskMgr.add(self.cameraTask, 'HxMouseLook::cameraTask')     
        
        #Task for changing direction/position 
        self.accept("w", setattr, [self, "forward", True])
        self.accept("shift-w", setattr, [self, "forward", True])
        self.accept("w-up", setattr, [self, "forward", False]) 
        self.accept("s", setattr, [self, "backward", True]) 
        self.accept("shift-s", setattr, [self, "backward", True]) 
        self.accept("s-up", setattr, [self, "backward", False])
        self.accept("a", setattr, [self, "left", True]) 
        self.accept("shift-a", setattr, [self, "left", True]) 
        self.accept("a-up", setattr, [self, "left", False]) 
        self.accept("d", setattr, [self, "right", True]) 
        self.accept("shift-d", setattr, [self, "right", True]) 
        self.accept("d-up", setattr, [self, "right", False]) 
        self.accept("r", setattr, [self, "up", True])
        self.accept("shift-r", setattr, [self, "up", True]) 
        self.accept("r-up", setattr, [self, "up", False])
        self.accept("f", setattr, [self, "down", True])
        self.accept("shift-f", setattr, [self, "down", True])
        self.accept("f-up", setattr, [self, "down", False]) 
        self.accept("q", setattr, [self, "rollLeft", True]) 
        self.accept("q-up", setattr, [self, "rollLeft", False]) 
        self.accept("e", setattr, [self, "rollRight", True]) 
        self.accept("e-up", setattr, [self, "rollRight", False])
        self.accept("shift", setattr, [self, "fast", 10.0])
        self.accept("shift-up", setattr, [self, "fast", 1.0])
        
        # setup collisions
        if self.collisionHandler != None:
            #setup collisions
            nearDist = self.camera.node().getLens().getNear()
            # Create a collision node for this camera.
            # and attach it to the camera.
            
            self.collisionNP = self.camera.attachNewNode(CollisionNode("firstPersonCamera"))
            
            # Attach a collision sphere solid to the collision node.
            self.collisionNP.node().addSolid(CollisionSphere(0, 0, 0, nearDist * 1.1))
            
#            self.collisionNP.show()
            # setup camera "from" bit-mask
            self.collisionNP.node().setFromCollideMask(self.collideMask)
            
            # add to collisionHandler (Pusher)
            self.collisionHandler.addCollider(self.collisionNP, self.camera)
            
            #add camera to collision system
            self.gameApp.cTrav.addCollider(self.collisionNP, self.collisionHandler)

    ## Stop to control the camera  
    def stop(self): 
        self.gameApp.taskMgr.remove("HxMouseLook::cameraTask") 
        
        mat = LMatrix4f(self.camera.getTransform(self.refNode).getMat())
        mat.invertInPlace()
        self.camera.setMat(LMatrix4f.identMat())
        self.gameApp.mouseInterfaceNode.setMat(mat)
        self.gameApp.enableMouse() 
        props = WindowProperties() 
        props.setCursorHidden(False) 
        self.gameApp.win.requestProperties(props)        
         
        self.forward = False 
        self.backward = False 
        self.left = False 
        self.right = False 
        self.up = False 
        self.down = False 
        self.rollLeft = False 
        
        self.ignore("w") 
        self.ignore("shift-w") 
        self.ignore("w-up") 
        self.ignore("s") 
        self.ignore("shift-s") 
        self.ignore("s-up") 
        self.ignore("a")
        self.ignore("shift-a") 
        self.ignore("a-up") 
        self.ignore("d")
        self.ignore("shift-d") 
        self.ignore("d-up") 
        self.ignore("r")
        self.ignore("shift-r")
        self.ignore("r-up") 
        self.ignore("f")
        self.ignore("shift-f")
        self.ignore("f-up") 
        self.ignore("q") 
        self.ignore("q-up") 
        self.ignore("e") 
        self.ignore("e-up")
        self.ignore("shift")
        self.ignore("shift-up")          
        
        # un-setup collisions
        if self.collisionHandler != None:
            # remove camera from the collision system
            self.gameApp.cTrav.removeCollider(self.collisionNP)
            # remove from collisionHandler (Pusher)
            self.collisionHandler.removeCollider(self.collisionNP)
            # remove the collision node
            self.collisionNP.removeNode() 
       
    ## Call to start/stop control system 
    def toggle(self): 
        if(self.running): 
            self.stop() 
            self.running = False 
        else: 
            self.start() 
            self.running = True 