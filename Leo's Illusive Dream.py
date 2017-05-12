# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 18:16:29 2016

@author: Dhruv
"""

from math import sin, cos
import sys
import time
from direct.showbase.ShowBase import ShowBase

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.interval.IntervalGlobal import Sequence
from direct.gui.DirectGui import *
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText 

from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import AmbientLight, TextNode
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import AmbientLight, TextNode, TextureStage, Texture
from panda3d.core import Material
from panda3d.core import *
from pandac.PandaModules import WindowProperties
from panda3d.core import ClockObject

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletHelper
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletSoftBodyConfig
from panda3d.bullet import ZUp

#from mainScreen import MainScreen

def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                    shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                    pos=(0.08, -pos - 0.04), align=TextNode.ALeft)
# Function to put title on the screen.

class CharacterController(ShowBase):
    def __init__(self):
        
        ShowBase.__init__(self)
        
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0, "zoom-in":0, "zoom-out":0, "wheel-in":0, "wheel-out":0, "fire":0}
        self.countCoin = {"count":0}
        self.mousebtn = [0,0,0]
        base.win.setClearColor(Vec4(0,0,0,1))
        # Create a frame
        frame = DirectFrame(text = "main", scale = 0.1, pos=(-1,0,1))
        # Add button
        self.bar = DirectWaitBar(text = "HEALTH", value = 500, scale = 0.3, range=500, pos = (0.5,0.5,0.9))
        
        #self.title = addTitle("Leo's Illusive Dream")
        
        
        self.inst4 = addInstructions(0.80, "[W]: Run Leo Forward")
        self.inst5 = addInstructions(0.75, "[Space]: Jump")
        self.inst6 = addInstructions(0.70, "[Rotate Mouse Left]: Rotate Leo's Camera Left")
        self.inst7 = addInstructions(0.65, "[Rotate Mouse Right]: Rotate Leo's Camera Right")
        self.inst8 = addInstructions(0.6, "Press E to shoot when enemy is close")
        self.inst9 = addInstructions(0.4, "Level1:Press 1")
        self.inst10 = addInstructions(0.3, "Level2:Press 2")
        
        
        # Adding Sound to the Game
        mySound = base.loader.loadSfx("models/sacrifice.wav")
        mySound.setLoop(True)
        mySound.play()
        #setup lights
        self.setupLights()
        self.countCoin11 = addInstructions(0.12, "Coins")
        # Input
        self.accept('escape', self.doExit)
        self.accept('r', self.doReset)
        self.accept('f3', self.toggleDebug)
        self.accept('space', self.doJump)
        self.accept("escape", sys.exit)
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("wheel_up", self.setKey, ["wheel-in", 1])
        self.accept("wheel_down", self.setKey, ["wheel-out", 1])
        self.accept("page_up", self.setKey, ["zoom-in", 1])
        self.accept("page_up-up", self.setKey, ["zoom-in", 0])
        self.accept("page_down", self.setKey, ["zoom-out", 1])
        self.accept("page_down-up", self.setKey, ["zoom-out", 0])
        self.accept("e", self.setKey, ["fire", 1])
        self.accept("e-up", self.setKey, ["fire", 0])
        self.accept("1",self.setlevel1)
        self.accept("2",self.setlevel2)
        
        # Task
        taskMgr.add(self.update, 'updateWorld')
        taskMgr.add(self.score, 'totalScore')
        
        self.isMoving = False
        self.isFire = False

        self.setup()
        base.setBackgroundColor(0.1, 0.1, 0.8, 1)
        base.setFrameRateMeter(True)
        #base.disableMouse()
        base.camera.reparentTo(self.characterNP)
        self.cameraTargetHeight = 6.0
        # How far should the camera be from Ralph
        self.cameraDistance = 30
        # Initialize the pitch of the camera
        self.cameraPitch = 10
        # This just disables the built in camera controls; we're using our own.
        base.disableMouse()
        # The mouse moves rotates the camera so lets get rid of the cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.loadBackground("models/ill.jpg")
        
    def doExit(self):
        self.cleanup()
        sys.exit(1)
        
    def doReset(self):
        self.cleanup()
        self.setup()
    def setlevel1(self):
        self.characterNP.setPos(-1, 0, 14)
    def setlevel2(self):
        self.characterNP.setPos(-228, -90, 28)
    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()
            #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value

    def doJump(self):
        self.character.setMaxJumpHeight(6.0)
        self.character.setJumpSpeed(8.0)
        self.character.doJump()
        
    def score(self, task):
        self.countCoin11.removeNode()
        
        self.countCoin11 = addInstructions(0.5, "Coins: "+str(self.countCoin.get("count")))
        
        return task.cont
        
    def ContactingBodies(self):
        # test for all the contacts in the bullet world
        manifolds = self.world.getManifolds() 
        for manifold in manifolds:    
                    
          
            if manifold.getNode1().getName()=="Enemy1" and manifold.getNode0().getName()=="Player":
                self.incBar(-2)   
            if manifold.getNode1().getName()=="Enemy2" and manifold.getNode0().getName()=="Player":
                self.incBar(-2)  
            if manifold.getNode1().getName()=="Enemy3" and manifold.getNode0().getName()=="Player":
                self.incBar(-2)  
            if manifold.getNode1().getName()=="Enemy4" and manifold.getNode0().getName()=="Player":
                self.incBar(-2)
              
            
    # Callback function to set text
    def incBar(self, arg):
    
        self.bar['value'] +=arg
        
    def removeBullet(self,task):
        for m in render.findAllMatches("**/=bullet"):
            m.removeNode()  
 
        return task.done
        
    def addFireInstruction(self,task):
        self.inst8 = addInstructions(0.3, "Press E to Fire")
        
        
        
        
        
    def createBullet(self):
        for i in range (1):    
            self.isFire = True
            self.obj = self.loader.loadModel("models/ball")
            self.obj.reparentTo(self.render)
            self.obj.setScale(0.2)
            self.obj.setPos(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ())
            self.obj.lookAt(self.characterNP.getPos())
            self.obj.setTag("bullet", str(i))
            bulletInterval1 = self.obj.posInterval(0.3, Point3(self.characterNP.getX()-10,self.characterNP.getY()-600,self.characterNP.getZ()),
                                                      startPos=Point3(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ()))
        
            bulletInterval1.start()
        
    def createBullet1(self):
        for i in range (1):    
            self.isFire = True
            self.obj = self.loader.loadModel("models/ball")
            self.obj.reparentTo(self.render)
            self.obj.setScale(0.2)
            self.obj.setPos(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ())
            self.obj.lookAt(self.characterNP.getPos())
            self.obj.setTag("bullet", str(i))
            bulletInterval2 = self.obj.posInterval(0.3, Point3(self.characterNP.getX(),self.characterNP.getY()-290,self.characterNP.getZ()),
                                                      startPos=Point3(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ()))
                    #bulletSequence.loop()
            bulletInterval2.start()
            
    def createBullet2(self):
        for i in range (1):    
            self.isFire = True
            self.obj = self.loader.loadModel("models/ball")
            self.obj.reparentTo(self.render)
            self.obj.setScale(0.2)
            self.obj.setPos(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ())
            self.obj.lookAt(self.characterNP.getPos())
            self.obj.setTag("bullet", str(i))
            bulletInterval2 = self.obj.posInterval(0.3, Point3(self.characterNP.getX()-10,self.characterNP.getY()-200,self.characterNP.getZ()),
                                                      startPos=Point3(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ()))
                    #bulletSequence.loop()
            bulletInterval2.start()
            
    def createBullet3(self):
        for i in range (1):    
            self.isFire = True
            self.obj = self.loader.loadModel("models/ball")
            self.obj.reparentTo(self.render)
            self.obj.setScale(0.2)
            self.obj.setPos(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ())
            self.obj.lookAt(self.characterNP.getPos())
            self.obj.setTag("bullet", str(i))
            bulletInterval2 = self.obj.posInterval(0.3, Point3(self.characterNP.getX()-90,self.characterNP.getY(),self.characterNP.getZ()),
                                                      startPos=Point3(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ()))
                    #bulletSequence.loop()
            bulletInterval2.start()
            
    def createBullet4(self):
        for i in range (1):    
            self.isFire = True
            self.obj = self.loader.loadModel("models/ball")
            self.obj.reparentTo(self.render)
            self.obj.setScale(0.2)
            self.obj.setPos(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ())
            self.obj.lookAt(self.characterNP.getPos())
            self.obj.setTag("bullet", str(i))
            bulletInterval2 = self.obj.posInterval(0.3, Point3(self.characterNP.getX(),self.characterNP.getY()+23,self.characterNP.getZ()),
                                                      startPos=Point3(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ()))
                    #bulletSequence.loop()
            bulletInterval2.start()
            
    
    
    def update(self, task):
        dt = globalClock.getDt()
        speed = Vec3(0, 0, 0)
        self.world.doPhysics(dt, 4, 1./240.)
        delayTime = 0.5
        self.ContactingBodies()
        
        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.characterNP)
        startpos = self.characterNP.getPos()
        
        #print "H "+str(self.characterNP.getH()) 
        #print "X"+str(self.characterNP.getX())
        #print "Y"+str(self.characterNP.getY())
         
        for coin in render.findAllMatches("**/=coin"):
            x = self.characterNP.getPos() - coin.getPos()
            if (x.length()) < 1.0:
                self.mySound = base.loader.loadSfx("models/coin.mp3")
        #self.mySound.setLoop(True)
                self.mySound.play()
                self.countCoin["count"] = self.countCoin.get("count") + 1
                coin.removeNode()
                
        for kill in render.findAllMatches("**/=bullet"):
            for killenemy in render.findAllMatches("**/=enemy"):
                z = self.obj.getPos() - self.characterNP1.getPos()
                if (z.length()) < 10.0:
                    kill.removeNode()
                    killenemy.removeNode()
                    
        for kill1 in render.findAllMatches("**/=bullet"):
            for killenemy1 in render.findAllMatches("**/=enemy1"):
                z = self.obj.getPos() - self.characterNP2.getPos()
                if (z.length()) < 5.0:
                    kill1.removeNode()
                    killenemy1.removeNode()
                    
        for kill2 in render.findAllMatches("**/=bullet"):
            for killenemy2 in render.findAllMatches("**/=enemy3"):
                z = self.obj.getPos() - self.characterNP3.getPos()
                if (z.length()) < 5.0:
                    kill2.removeNode()
                    killenemy2.removeNode()
                    
        for kill3 in render.findAllMatches("**/=bullet"):
            for killenemy3 in render.findAllMatches("**/=enemy4"):
                z = self.obj.getPos() - self.characterNP4.getPos()
                if (z.length()) < 5.0:
                    kill3.removeNode()
                    killenemy3.removeNode()
                
        self.checkHeight()
        # If a move-key is pressed, move Leo in the specified direction.

        if (self.keyMap["left"]!=0):
            self.characterNP.setH(self.characterNP.getH() + 300 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.characterNP.setH(self.characterNP.getH() - 300 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.characterNP.setY(self.characterNP, -25 * globalClock.getDt())
            
        #fire1
        y = self.characterNP.getPos() - self.characterNP1.getPos()
        if (y.length()) < 40.0:
            
            
           # taskMgr.doMethodLater(50,self.removeFireInstruction,'removeFireInstruction')
            
            
            if (self.characterNP.getH()> -10 and self.characterNP.getH()< 10 and self.keyMap["fire"]!=0):
                self.createBullet()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
                
            if (self.characterNP.getH()> -10 and self.characterNP.getH()< 20 and self.keyMap["fire"]!=0):
                self.createBullet1()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
            
            if (self.characterNP.getH()> -9 and self.characterNP.getH()< 0 and self.keyMap["fire"]!=0):
                self.createBullet2()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
                
        #fire2
        r = self.characterNP.getPos() - self.characterNP2.getPos()
        if (r.length()) < 40.0:
            
                        
            if (self.characterNP.getH()> -100 and self.characterNP.getH()< -85 and self.keyMap["fire"]!=0):
                self.createBullet3()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
            if (self.characterNP.getH()> -10 and self.characterNP.getH()< 20 and self.keyMap["fire"]!=0):
                self.createBullet1()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
            
            if (self.characterNP.getH()> -9 and self.characterNP.getH()< 0 and self.keyMap["fire"]!=0):
                self.createBullet2()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
                
        #fire3
        r = self.characterNP.getPos() - self.characterNP3.getPos()
        if (r.length()) < 40.0:
            
                        
            if (self.characterNP.getH()> -100 and self.characterNP.getH()< -85 and self.keyMap["fire"]!=0):
                self.createBullet3()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
                
        #fire4
        r = self.characterNP.getPos() - self.characterNP4.getPos()
        if (r.length()) < 40.0:
            
                        
            if (self.characterNP.getH()> -180 and self.characterNP.getH()< -60 and self.keyMap["fire"]!=0):
                self.createBullet4()
                taskMgr.doMethodLater(delayTime, self.removeBullet, 'removeBullet')
           
            
        # If a zoom button is pressed, zoom in or out
        if (self.keyMap["wheel-in"]!=0):
            self.cameraDistance -= 0.1 * self.cameraDistance;
            if (self.cameraDistance < 10):
                self.cameraDistance = 10
            self.keyMap["wheel-in"] = 0
        elif (self.keyMap["wheel-out"]!=0):
            self.cameraDistance += 0.1 * self.cameraDistance;
            if (self.cameraDistance > 50):
                self.cameraDistance = 50
            self.keyMap["wheel-out"] = 0
        if (self.keyMap["zoom-in"]!=0):
            self.cameraDistance -= globalClock.getDt() * self.cameraDistance;
            if (self.cameraDistance < 10):
                self.cameraDistance = 10
        elif (self.keyMap["zoom-out"]!=0):
            self.cameraDistance += globalClock.getDt() * self.cameraDistance;
            if (self.cameraDistance > 50):
                self.cameraDistance = 50
            
        if base.mouseWatcherNode.hasMouse():
            # get changes in mouse position
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            deltaX = md.getX() - 200
            deltaY = md.getY() - 200
            # reset mouse cursor position
            base.win.movePointer(0, 200, 200)
            # alter Leo's yaw by an amount proportionate to deltaX
            self.characterNP.setH(self.characterNP.getH() - 0.3* deltaX)
            # find the new camera pitch and clamp it to a reasonable range
            self.cameraPitch = self.cameraPitch + 0.1 * deltaY
            if (self.cameraPitch < -60): self.cameraPitch = -60
            if (self.cameraPitch >  80): self.cameraPitch =  80
            base.camera.setHpr(0,self.cameraPitch,0)
            # set the camera at around Leo's middle
            # We should pivot around here instead of the view target which is noticebly higher
            base.camera.setPos(0,0,self.cameraTargetHeight/2)
            # back the camera out to its proper distance
            base.camera.setY(base.camera,self.cameraDistance)
        
        # point the camera at the view target
        viewTarget = Point3(0,0,self.cameraTargetHeight)
        base.camera.lookAt(viewTarget)
        
        # If Leo is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.actorNP.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.actorNP.stop()
                self.actorNP.pose("walk",5)
                self.isMoving = False
      
        return task.cont

    def cleanup(self):
        self.world = None
        self.render.removeNode()
        
    def checkHeight(self):
        if (self.characterNP.getZ()) < 6:
            #add some text
            output = "Game Over You Died!!Run the program again"
            textObject = OnscreenText(text = output, pos = (0.09,-0.08),
            scale = 0.1,fg=(1,2,2,1),align=TextNode.ACenter,mayChange=1)
            self.incBar(-50)
            
    def win(self):
            #add some text
            manifolds = self.world.getManifolds() 
            for manifold in manifolds:    
                    
          
                if manifold.getNode1().getName()=="plank16" and manifold.getNode0().getName()=="Player":
                    output = "You Win"
                    textObject = OnscreenText(text = output, pos = (0.09,-0.08),
                    scale = 0.1,fg=(1,2,2,1),align=TextNode.ACenter,mayChange=1)
            
    def setupLights(self):
        # Light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alightNP = render.attachNewNode(alight)

        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(1, 1, -1))
        dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlightNP = render.attachNewNode(dlight)

        self.render.clearLight()
        self.render.setLight(alightNP)
        self.render.setLight(dlightNP)
        
# Function to add default background image (Sky)
    def loadBackground(self, imagepath):
        
        self.background = OnscreenImage(parent=render2dp, image= imagepath)
        base.cam2dp.node().getDisplayRegion(0).setSort(-20)


    def setup(self):
        # World
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        #self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())
        
         # Floor
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        floorNP = self.render.attachNewNode(BulletRigidBodyNode('Floor'))
        floorNP.node().addShape(shape)
        floorNP.setPos(0, 0, 0)
        floorNP.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(floorNP.node())
    
        # wall texture1
        
        self.grass = loader.loadModel("models/square")
        self.grass.reparentTo(render)
        self.grass.setPos(0, 20, 0)
        self.grass.setHpr(0,90,0)
        self.grass.setScale(500,500,1)
        self.coin_tex = self.loader.loadTexture("models/ill.jpg")
        self.grass.setTexture(self.coin_tex,1)
        
       
        
        #wall texture4
        
        self.grass = loader.loadModel("models/square")
        self.grass.reparentTo(render)
        self.grass.setPos(0, -350, 0)
        self.grass.setHpr(0,-90,0)
        self.grass.setScale(500,500,1)
        self.coin_tex = self.loader.loadTexture("models/ill.jpg")
        self.grass.setTexture(self.coin_tex,1)
        self.grass.setTwoSided(True)
        #Plank 1
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(40,5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(0, 0, 10)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(80, 10, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        #Plank 2
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(5,40,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-85, -45, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10, 80, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-84, -50, 24)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
           
        
        
        #Plank 3
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(2.7,2.7,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath1 = self.render.attachNewNode(floorNode)
        floorNodePath1.setCollideMask(BitMask32.allOn())
        floorNodePath1.setPos(-95, -80, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath1.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(5, 5, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath1)
        model1PosInterval1 = floorNodePath1.posInterval(13, Point3(-95, -70, 20),
                                                            startPos=Point3(-95, -80, 20))
        model1PosInterval2 = floorNodePath1.posInterval(13, Point3(-95, -80, 20),
                                                            startPos=Point3(-95, -70, 20))
        self.modelPace1 = Sequence(model1PosInterval1, model1PosInterval2,name="modelPace-2")
        self.modelPace1.loop()
        
        
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-95, -80, 24)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        
        #Plank 4
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(2.7,2.7,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath2 = self.render.attachNewNode(floorNode)
        floorNodePath2.setCollideMask(BitMask32.allOn())
        floorNodePath2.setPos(-105, -80, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath2.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(5, 5, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath2)
        
        model2PosInterval1 = floorNodePath2.posInterval(13, Point3(-105, -80, 20),
                                                            startPos=Point3(-105, -70, 20))
        model2PosInterval2 = floorNodePath2.posInterval(13, Point3(-105, -70, 20),
                                                            startPos=Point3(-105, -80, 20))
        self.modelPace2 = Sequence(model2PosInterval1, model2PosInterval2,name="modelPace-3")
        self.modelPace2.loop()
        
        #Plank 5
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(2.7,2.7,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath3 = self.render.attachNewNode(floorNode)
        floorNodePath3.setCollideMask(BitMask32.allOn())
        floorNodePath3.setPos(-115, -80, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath3.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(5, 5, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath3)
        
        model3PosInterval1 = floorNodePath3.posInterval(13, Point3(-115, -70, 20),
                                                            startPos=Point3(-115, -80, 20))
        model3PosInterval2 = floorNodePath3.posInterval(13, Point3(-115, -80, 20),
                                                            startPos=Point3(-115, -70, 20))
        self.modelPace3 = Sequence(model3PosInterval1, model3PosInterval2,name="modelPace-4")
        self.modelPace3.loop()
        for i in range (1):
            coinModel = self.loader.loadModel('models/emerald')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-115, -80, 24)
            coinModel.setScale(0.008)
            coin_tex = self.loader.loadTexture("models/emeraldtexture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        
        #Plank 6
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(2.7,2.7,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath4 = self.render.attachNewNode(floorNode)
        floorNodePath4.setCollideMask(BitMask32.allOn())
        floorNodePath4.setPos(-125, -80, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath4.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(5, 5, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath4)
        
        model4PosInterval1 = floorNodePath4.posInterval(13, Point3(-125, -80, 20),
                                                            startPos=Point3(-125, -70, 20))
        model4PosInterval2 = floorNodePath4.posInterval(13, Point3(-125, -70, 20),
                                                            startPos=Point3(-125, -80, 20))
        self.modelPace4 = Sequence(model4PosInterval1, model4PosInterval2,name="modelPace-5")
        self.modelPace4.loop()
        
        #Plank 7
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(2.7,2.7,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-135, -80, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(5, 5, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        #Plank 9
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(25,2,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-140, -10, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(50, 4, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        for i in range (1):
            coinModel = self.loader.loadModel('models/emerald')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-140, -10, 24)
            coinModel.setScale(0.008)
            coin_tex = self.loader.loadTexture("models/emeraldtexture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
            
        for i in range (1):
            coinModel = self.loader.loadModel('models/emerald')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-130, -10, 24)
            coinModel.setScale(0.008)
            coin_tex = self.loader.loadTexture("models/emeraldtexture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        
        #Moving plank
        
        #Plank 8
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(2.7,2.7,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-118, -10, 20) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(5, 5, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        modelPosInterval1 = floorNodePath.posInterval(13, Point3(-135, -75, 20),
                                                            startPos=Point3(-118, -10, 20))
        modelPosInterval2 = floorNodePath.posInterval(13, Point3(-118, -10, 20),
                                                            startPos=Point3(-135, -75, 20))
        self.modelPace = Sequence(modelPosInterval1, modelPosInterval2,name="modelPace-1")
        self.modelPace.loop()
        
         #Plank 10
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(40,5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-215, -90, 27)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(80, 10, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        self.level = loader.loadModel("models/square")
        self.level.reparentTo(self.render)
        self.level.setPos(-230, -90, 28)
        self.level.setHpr(0,0,90)
        self.level.setScale(10,10,1)
        self.level_tex = self.loader.loadTexture("models/brick1.png")
        self.level.setTexture(self.level_tex,1)
        self.level.setTwoSided(True)
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-218, -90, 29)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-200, -90, 29)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-185, -90, 29)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-170, -90, 27)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-157, -90, 26)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-140, -90, 24)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        for i in range (1):
            coinModel = self.loader.loadModel('models/coin')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-135, -90, 23)
            coinModel.setScale(0.6)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex, 1)
            coinModel.setHpr(0, 0, -90)
            coinModel.setTag("coin", str(i))
        
        
        
        #Plank 11
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(15,5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-280, -90, 27)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(30, 10, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        #Plank 12
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(2.5,2.5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-302, -90, 27)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(5, 5, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        model7PosInterval1 = floorNodePath.posInterval(6, Point3(-302, -90, 24),
                                                            startPos=Point3(-302, -90, 27))
        model7PosInterval2 = floorNodePath.posInterval(6, Point3(-302, -90, 27),
                                                            startPos=Point3(-302, -90, 24))
        self.modelPace7 = Sequence(model7PosInterval1, model7PosInterval2,name="modelPace-8")
        self.modelPace7.loop()
        
        #Plank 13
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(2.5,2.5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-312, -90, 24)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(5, 5, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        model8PosInterval1 = floorNodePath.posInterval(6, Point3(-312, -90, 27),
                                                            startPos=Point3(-312, -90, 24))
        model8PosInterval2 = floorNodePath.posInterval(6, Point3(-312, -90, 24),
                                                            startPos=Point3(-312, -90, 27))
        self.modelPace8 = Sequence(model8PosInterval1, model8PosInterval2,name="modelPace-9")
        self.modelPace8.loop()
        
        #Plank 14
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(2.5,2.5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-322, -90, 27)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(5, 5, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        model9PosInterval1 = floorNodePath.posInterval(6, Point3(-322, -90, 24),
                                                            startPos=Point3(-322, -90, 27))
        model9PosInterval2 = floorNodePath.posInterval(6, Point3(-322, -90, 27),
                                                            startPos=Point3(-322, -90, 24))
        self.modelPace9 = Sequence(model9PosInterval1, model9PosInterval2,name="modelPace-10")
        self.modelPace9.loop()
        
        #Plank 15
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(2.5,2.5,1))
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-332, -90, 24)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(5, 5, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        model10PosInterval1 = floorNodePath.posInterval(6, Point3(-332, -90, 27),
                                                            startPos=Point3(-332, -90, 24))
        model10PosInterval2 = floorNodePath.posInterval(6, Point3(-332, -90, 24),
                                                            startPos=Point3(-332, -90, 27))
        self.modelPace10 = Sequence(model10PosInterval1, model10PosInterval2,name="modelPace-11")
        self.modelPace10.loop()
        
        #Plank 16
        size = Vec3(2, 5, 1)
        shape = BulletBoxShape(Vec3(2.5,2.5,1))
        floorNode = BulletRigidBodyNode('plank16')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-350, -30, 27)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(5, 5, 1)
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        
        #Plank 17
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(5,40,1)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-340, -60, 27) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/brick.egg")
        floorModel.setScale(10, 80, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        """
        self.grass = loader.loadModel("models/square")
        self.grass.reparentTo(render)
        self.grass.setPos(-340, -60, 0)
        self.grass.setHpr(-90,0,0)
        self.grass.setScale(1000,1000,1)
        self.coin_tex = self.loader.loadTexture("models/ill.jpg")
        self.grass.setTexture(self.coin_tex,1)
        self.grass.setTwoSided(True)
        """
        #walltext6
        self.grass = loader.loadModel("models/square")
        self.grass.reparentTo(render)
        self.grass.setPos(-245, 120, 0)
        self.grass.setHpr(0,0,-90)
        self.grass.setScale(200,200,1)
        self.coin_tex = self.loader.loadTexture("models/ill.jpg")
        self.grass.setTexture(self.coin_tex,1)
        #self.grass.setTwoSided(True)
        #walltext7
        self.grass = loader.loadModel("models/square")
        self.grass.reparentTo(render)
        self.grass.setPos(-180, -40, 0)
        self.grass.setHpr(0,0,-90)
        self.grass.setScale(1000,1000,1)
        self.coin_tex = self.loader.loadTexture("models/ill.jpg")
        self.grass.setTexture(self.coin_tex,1)
        
        
        #disk platform 1 
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(6,6,0.5)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-140, -90, 21) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/disk.egg")
        floorModel.setScale(3, 3, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
    #disk platform 2 
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(6,6,0.5)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-150, -90, 23) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/disk.egg")
        floorModel.setScale(3, 3, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        #disk platform 3 
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(6,6,0.5)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-160, -90, 24.5) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/disk.egg")
        floorModel.setScale(3, 3, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        #disk platform 4 
        size = Vec3(2, 5, 1) #2,5,1
        shape = BulletBoxShape(Vec3(6,6,0.5)) #40,5,1
        floorNode = BulletRigidBodyNode('Floor')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-170, -90, 26.5) #-131,0,20
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/disk.egg")
        floorModel.setScale(3, 3, 1) #80, 10, 1
        floorModel.setPos(0, 0, 0)
        floorModel.reparentTo(floorNodePath)
        
        #stairs1
        origin = Point3(2, 0, 1)  #10,0,1
        size = Vec3(4, 4.75, 0.5)   #4,4.75,1
        shape = BulletBoxShape(size * 0.55)
        
        for i in range(10):
            i=i + 5
            pos = origin*i + size * i
            pos.setY(0)
            pos.setX(pos.getX()*-1)
            stairNP = self.render.attachNewNode(BulletRigidBodyNode('Stair%i' % i))
            stairNP.node().addShape(shape)
            stairNP.setPos(pos)
            stairNP.setCollideMask(BitMask32.allOn())
            modelNP = loader.loadModel('models/box.egg')
            modelNP.reparentTo(stairNP)
            modelNP.setPos(-size.x/2.0, -size.y/2.0, -size.z/3.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(stairNP.node())
            if (i%2 == 0):
                coinModel = self.loader.loadModel('models/coin')
                coinModel.reparentTo(self.render)
                coinModel.setPos(pos+1)
                coinModel.setScale(0.6)
                coin_tex = loader.loadTexture("models/coin-texture.jpg")
                coinModel.setTexture(coin_tex, 1)
                coinModel.setHpr(0, 0, -90)
                coinModel.setTag("coin",str(i))

         # Character
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(-1, 0, 14)
        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)
        self.character.setGravity(20)

        self.actorNP = Actor('models/ralph/ralph.egg', {
                         'run' : 'models/ralph/ralph-run.egg',
                         'walk' : 'models/ralph/ralph-walk.egg',
                         'jump' : 'models/ralph/ralph-jump.egg'})

        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.378)
        self.actorNP.setH(-21)
        self.actorNP.setPos(0, 0, -1)
        #enemy1
        for i in range (1):
            size = Vec3(1, 1, 8)
            shape = BulletBoxShape(size * 0.55)
            self.character1 = BulletRigidBodyNode('Enemy1')
            self.character1.addShape(shape)
            self.characterNP1 = self.render.attachNewNode(self.character1)
            self.characterNP1.setPos(-85, -45, 21)
            self.characterNP1.setH(45)
            self.characterNP1.setCollideMask(BitMask32.allOn())
            self.world.attachRigidBody(self.character1)
            self.character1.setGravity(20)
            self.actorNP1 = Actor('models/beefy/beefy.egg', {
                             'idle' : 'models/beefy/ralph-idle.egg',
                             'walk' : 'models/beefy/beefy-walk.egg'})
            self.actorNP1.reparentTo(self.characterNP1)
            self.actorNP1.setScale(0.2)
            self.actorNP1.setH(-25)
            self.actorNP1.setPos(0, 0, 2)
            self.characterNP1.setTag("enemy", str(i))
        enemy1PosInterval1 = self.characterNP1.posInterval(7, Point3(-85, -75, 21),
                                                        startPos=Point3(-85, -45, 21))
        enemy1HprInterval1 = self.actorNP1.hprInterval(1.5, Point3(self.actorNP1.getH()+180, self.actorNP1.getP(), self.actorNP1.getR()),
                                                       startHpr=self.actorNP1.getHpr())
        enemy1PosInterval2 = self.characterNP1.posInterval(7, Point3(-85, -45, 21),
                                                        startPos=Point3(-85, -75, 21))
        enemy1HprInterval2 = self.actorNP1.hprInterval(1.5, Point3(0, 0, 0),
                                                        startHpr=Point3(180, 0, 0))                                                    
        self.enemy1Pace = Sequence(enemy1PosInterval1, enemy1HprInterval1,  enemy1PosInterval2, enemy1HprInterval2, name="enemy1")
        self.enemy1Pace.loop()
        self.actorNP1.loop("walk")
        
        #enemy2
        for i in range (1):
            size = Vec3(1, 1, 8)
            shape = BulletBoxShape(size * 0.55)
            self.character2 = BulletRigidBodyNode('Enemy2')
            self.character2.addShape(shape)
            self.characterNP2 = self.render.attachNewNode(self.character2)
            self.characterNP2.setPos(-215, -90, 27)
            self.characterNP2.setH(45)
            self.characterNP2.setCollideMask(BitMask32.allOn())
            self.world.attachRigidBody(self.character2)
            self.character2.setGravity(20)
            self.actorNP2 = Actor('models/beefy/beefy.egg', {
                             'idle' : 'models/beefy/ralph-idle.egg',
                             'walk' : 'models/beefy/beefy-walk.egg'})
            self.actorNP2.reparentTo(self.characterNP2)
            self.actorNP2.setScale(0.2)
            self.actorNP2.setH(-40)
            self.actorNP2.setPos(0, 0, 3)
            self.characterNP2.setTag("enemy1", str(i))
        enemy2PosInterval1 = self.characterNP2.posInterval(7, Point3(-195, -90, 27),
                                                        startPos=Point3(-215, -90, 27))
        enemy2HprInterval1 = self.actorNP2.hprInterval(1.5, Point3(self.actorNP2.getH()+270, self.actorNP2.getP(), self.actorNP2.getR()),
                                                       startHpr=self.actorNP2.getHpr())
        enemy2PosInterval2 = self.characterNP2.posInterval(7, Point3(-215, -90, 27),
                                                        startPos=Point3(-195, -90, 27))
        enemy2HprInterval2 = self.actorNP2.hprInterval(1.5, Point3(0, 0, 0),
                                                        startHpr=Point3(270, 0, 0))                                                    
        self.enemy2Pace = Sequence(enemy2PosInterval1, enemy2HprInterval1,  enemy2PosInterval2, enemy2HprInterval2, name="enemy2")
        self.enemy2Pace.loop()
        self.actorNP2.loop("walk")
        
        #enemy3
        for i in range (1):
            size = Vec3(1, 1, 8)
            shape = BulletBoxShape(size * 0.55)
            self.character3 = BulletRigidBodyNode('Enemy3')
            self.character3.addShape(shape)
            self.characterNP3 = self.render.attachNewNode(self.character3)
            self.characterNP3.setPos(-280, -90, 27)
            self.characterNP3.setH(45)
            self.characterNP3.setCollideMask(BitMask32.allOn())
            self.world.attachRigidBody(self.character3)
            self.character3.setGravity(20)
            self.actorNP3 = Actor('models/beefy/beefy.egg', {
                             'idle' : 'models/beefy/ralph-idle.egg',
                             'walk' : 'models/beefy/beefy-walk.egg'})
            self.actorNP3.reparentTo(self.characterNP3)
            self.actorNP3.setScale(0.2)
            self.actorNP3.setH(-40)
            self.actorNP3.setPos(0, 0, 3)
            self.characterNP3.setTag("enemy3", str(i))
        enemy3PosInterval1 = self.characterNP3.posInterval(7, Point3(-270, -90, 27),
                                                        startPos=Point3(-280, -90, 27))
        enemy3HprInterval1 = self.actorNP3.hprInterval(1.5, Point3(self.actorNP3.getH()+270, self.actorNP3.getP(), self.actorNP3.getR()),
                                                       startHpr=self.actorNP3.getHpr())
        enemy3PosInterval2 = self.characterNP3.posInterval(7, Point3(-280, -90, 27),
                                                        startPos=Point3(-270, -90, 27))
        enemy3HprInterval2 = self.actorNP3.hprInterval(1.5, Point3(0, 0, 0),
                                                        startHpr=Point3(270, 0, 0))                                                    
        self.enemy3Pace = Sequence(enemy3PosInterval1, enemy3HprInterval1,  enemy3PosInterval2, enemy3HprInterval2, name="enemy3")
        self.enemy3Pace.loop()
        self.actorNP3.loop("walk")
        
        #enemy4
        for i in range (1):
            size = Vec3(1, 1, 8)
            shape = BulletBoxShape(size * 0.55)
            self.character4 = BulletRigidBodyNode('Enemy4')
            self.character4.addShape(shape)
            self.characterNP4 = self.render.attachNewNode(self.character4)
            self.characterNP4.setPos(-340, -60, 27)
            self.characterNP4.setH(45)
            self.characterNP4.setCollideMask(BitMask32.allOn())
            self.world.attachRigidBody(self.character4)
            self.character4.setGravity(20)
            self.actorNP4 = Actor('models/beefy/beefy.egg', {
                             'idle' : 'models/beefy/ralph-idle.egg',
                             'walk' : 'models/beefy/beefy-walk.egg'})
            self.actorNP4.reparentTo(self.characterNP4)
            self.actorNP4.setScale(0.2)
            self.actorNP4.setH(-40)
            self.actorNP4.setPos(0, 0, 3)
            self.characterNP4.setTag("enemy4", str(i))
        enemy4PosInterval1 = self.characterNP4.posInterval(7, Point3(-340, -70, 27),
                                                        startPos=Point3(-340, -90, 27))
        enemy4HprInterval1 = self.actorNP4.hprInterval(1.5, Point3(self.actorNP4.getH(), self.actorNP4.getP(), self.actorNP4.getR()),
                                                       startHpr=self.actorNP4.getHpr())
        enemy4PosInterval2 = self.characterNP4.posInterval(7, Point3(-340, -90, 27),
                                                        startPos=Point3(-340, -70, 27))
        enemy4HprInterval2 = self.actorNP4.hprInterval(1.5, Point3(150, 0, 0),
                                                        startHpr=Point3(0, 0, 0))                                                    
        self.enemy4Pace = Sequence(enemy4PosInterval1, enemy4HprInterval1,  enemy4PosInterval2, enemy4HprInterval2, name="enemy4")
        self.enemy4Pace.loop()
        self.actorNP4.loop("walk")
        

game = CharacterController()
game.run()

