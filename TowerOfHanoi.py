#
#  t o w e r . p y
#
#  Copyright 2001 by Chris Meyers.
#
from robomaster import robot
from robomaster import led
import time

# Relevant Measurements
# Peg height = 14.6 account for .2 cm error

# Block height = 3.8 (in object)

# 8 cm from the blocks

# First block (190,-70) (may want to make base a bit thicker)

# second block (201, -40) (dependent on the base height (maybe 190)

# third block (200,-7) (dependent on the base height (maybe 190)

# Clearance height 204,67

# Base height =0.7 (in object)

# Upper bd first block = 3.8 + baseheight       (
# Lower bd first block = baseheight

# Upper bd second block = 3.8 * 2 + baseheight
# Lower bd second block = Upper bd first block

# Upper bd third block = 3.8 * 3 + baseheight
# Lower bd third block = Upper bd second block

# peg distance = 32 cm (in object)

class Tower:
    def __init__ (self, num_disks):
        self.counter = num_disks

    def add(self):
        self.counter += 1

    def sub(self):
        self.counter -= 1


class pegMove :
    def __init__ (self, name, peg, newPeg):
        self.name = name
        self.peg = peg
        # This value is hardcoded in m
        self.distance = 0.32
        self.baseHeight = 0.007
        self.blockHeight = 0.038

        
        self.newPeg = newPeg
    def move(self,TowerList,ep_robot):
        # We must decide to move units to the left or right first.
        # A -> C
        # Pegs are labelled 1,2,3
        # We do this by final - intitial. 
        pegFactor = self.newPeg - self.peg      #+ve means right, -ve means left
        distance = pegFactor * self.distance    # The distance to move in cm
        
        # Call Robomaster Functions
        ep_arm = ep_robot.robotic_arm
        ep_gripper = ep_robot.gripper
        ep_chassis = ep_robot.chassis

        # Grab
        grabHeight = TowerList[self.peg - 1].counter * self.blockHeight + self.baseHeight                                  # newPeg -1 is the proper index for the give
        
        # Move ep arm to the proper height for grab
        if TowerList[self.peg-1].counter ==1:
            ep_arm.moveto(190,-70)
        elif TowerList[self.peg-1].counter == 2:
            ep_arm.moveto(201,-40)
        elif TowerList[self.peg-1].counter == 3:
            ep_arm.moveto(200,-7)

        time.sleep(2)
        ep_gripper.close(50)
        time.sleep(2)
                   
        TowerList[self.peg - 1].sub()
        # Clear the peg
        ep_arm.moveto(204,67)

        time.sleep(2)
        
        # move
        ep_chassis.move(x=0, y=self.distance, z=0, xy_speed=0.30, z_speed=30).wait_for_completed()   # May need to tweak

        # Place
        
        placeheight = TowerList[self.newPeg - 1].counter * self.blockHeight + self.baseHeight                                  # newPeg -1 is the proper index for the give

        if TowerList[self.newPeg-1].counter ==1:
            ep_arm.moveto(190,-70)
        elif TowerList[self.newPeg-1].counter == 2:
            ep_arm.moveto(201,-40)
        elif TowerList[self.newPeg-1].counter == 3:
            ep_arm.moveto(200,-7)
        
        time.sleep(2)
        ep_gripper.open(50)
        time.sleep(2)
        
        TowerList[self.newPeg - 1].add()


class disc :
    # create a disc, assigning it a name (so we can watch it better)
    # an initial peg, and a reference to the next smaller disc
    # or the value None if this is to be the smallest disc
    def __init__ (self, name, peg, nextSmaller) :
        self.name = name
        self.peg  = peg
        self.nextSmaller = nextSmaller
    # when asked to move to a new peg, find the alternate peg by starting
    # with a list of all 3 and removing the 2 I can't use.
    # then move everything above me to the alternate peg
    # then move myself (change my peg value).
    # Finally move the smaller pegs back on top of me
    def move (self,newPeg,TowerList,ep_robot) :
        print(self.name + " : I have been requested to move to peg %s" %  newPeg)
        if self.nextSmaller :
            pegs = [1,2,3]           # find what has to be the alternate peg
            pegs.remove(newPeg)      # can't be the one I'm going to
            pegs.remove(self.peg)    # can't be the one we're on
            altPeg = pegs[0]         # Ahh. That one.
            print(self.name+" : Asking " + self.nextSmaller.name +
                             " to get out of my way and move to peg %s" % altPeg)
            self.nextSmaller.move(altPeg,TowerList,ep_robot)
            print(self.name + " : Moving to %s" % newPeg)
            self.peg = newPeg
            print(self.name + " : Asking " + self.nextSmaller.name +
                                " to rejoin me on peg %s" % self.peg)
            self.nextSmaller.move(self.peg,TowerList,ep_robot)
        else :
            # If I'm the smallest disc, life is very simple
            print(self.name +  " : Moving to %s" % newPeg)
            thisMove = pegMove(self.name, self.peg, newPeg)
            thisMove.move(TowerList,ep_robot)

            # Pegs are labelled 1,2,3
            TowerList[self.peg - 1].sub()
            TowerList[newPeg - 1].add()

            
            print("State: " + str(TowerList[0].counter),str(TowerList[1].counter),str(TowerList[2].counter))

            self.peg = newPeg
# Make 3 discs all on peg 1. 'A' is the largest and on the bottom
def test() :

    ep_robot = robot.Robot()
    try:

        # 指定连接方式为AP 直连模式
        ep_robot.initialize(conn_type='ap')

        ep_arm = ep_robot.robotic_arm
        ep_gripper = ep_robot.gripper

        ep_gripper.open(50)
        time.sleep(2)
        ep_arm.recenter()
        time.sleep(2)

        TowerList = []
        Tower1 = Tower(3)
        Tower2 = Tower(0)
        Tower3 = Tower(0)
        TowerList.append(Tower1)
        TowerList.append(Tower2)
        TowerList.append(Tower3)

        print("State: " + str(TowerList[0].counter),str(TowerList[1].counter),str(TowerList[2].counter))

        c = disc("C",1, None)   # the smallest disc. No nextSmaller disc
        b = disc("B",1, c)      # 2nd largest disc
        a = disc("A",1, b)      # largest disc

        a.move(3,TowerList,ep_robot)               # Now move all the discs to peg 3
   
    except Exception as e:
        print(e)



if __name__ == "__main__" : test()
