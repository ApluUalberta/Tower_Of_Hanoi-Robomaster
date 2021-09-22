#
#  t o w e r . p y
#

from robomaster import robot
from robomaster import led
import time


class RoboMaster :
    def __init__ (self,ep_robot,peg) :
        self.ep_ledrun = ep_robot.led
        self.ep_arm = ep_robot.robotic_arm
        self.ep_gripper = ep_robot.gripper
        self.ep_chassis = ep_robot.chassis

        self.peg  = peg
    def setPeg(self,myPeg):
        self.peg = myPeg
    
    def moveHorizontally(self,displacement):
        self.ep_chassis.move(x=0, y=displacement, z=0, xy_speed=0.30, z_speed=30).wait_for_completed()   # May need to tweak
    
    def moveArm(self,x,y):
        self.ep_arm.moveto(x,y)
    def gripperClose(self):
        self.ep_gripper.close(100)
    
    def gripperOpen(self):
        self.ep_gripper.open(100)


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

    def robotMove(self,newPeg,robomaster):
        '''
        resetFactor = self.peg - robomaster.peg

        displacement = resetFactor * hardcodedPegDistance in mm

        robot.move(x=displacement....)

        # Now, we should be located at self.peg.
        # So, we can move to newPeg

        moveFactor = newPeg - self.peg

        displacement = resetFactor * hardcodedPegDistance in mm

        '''
        
        print("--------------------------Moving to peg---------------------------------")
        print("------------------------------------------------------------------------")

        resetFactor = self.peg - robomaster.peg
        displacement = resetFactor * 0.28

        
        print("self.peg: " + str(self.peg), "robomaster: " + str(robomaster.peg))
        print("ResetFactor: " + str(resetFactor), "Displacement: " + str(displacement))
        robomaster.moveHorizontally(displacement)
        

        # Now, we should be located at self.peg.
        print(" ")
        print(" ")
        
        robomaster.peg = self.peg 
        print("------------------------Moving disc-------------------------------------")
        print("------------------------------------------------------------------------")
        # So, we can move to newPeg

        moveFactor = newPeg - robomaster.peg
        displacement = moveFactor * 0.28
        print("newPeg: " + str(newPeg), "self.peg: " + str(self.peg), "robomaster: " + str(robomaster.peg))
        print("moveFactor: " + str(moveFactor), "Displacement: " + str(displacement))

        robomaster.moveHorizontally(displacement)
        print(" ")
        print(" ")

    def move (self,newPeg,RoboMaster) :
        print(self.name + " : I have been requested to move to peg %s" %  newPeg)
        if self.nextSmaller :
            pegs = [1,2,3]           # find what has to be the alternate peg
            pegs.remove(newPeg)      # can't be the one I'm going to
            pegs.remove(self.peg)    # can't be the one we're on
            altPeg = pegs[0]         # Ahh. That one.

            print(self.name+" : Asking " + self.nextSmaller.name +
                             " to get out of my way and move to peg %s" % altPeg)
            self.nextSmaller.move(altPeg,RoboMaster)

            print(" ")
            print(" ")

            print(self.name + " :(move1) Moving to %s" % newPeg)
            # Do stuff before updating the position
            # The robot is in a given position, we want it to move to self.peg from the robot's given peg
            # Get the robot's peg position
            # Right is positive, left is negative

            self.robotMove(newPeg,RoboMaster)

            RoboMaster.peg = newPeg

            self.peg = newPeg   # Update the position.
            # Do after updating the position
            

            print(self.name + " : Asking " + self.nextSmaller.name +
                                " to rejoin me on peg %s" % self.peg)
            self.nextSmaller.move(self.peg,RoboMaster)
        else :
            # If I'm the smallest disc in the stack
            print(" ")
            print(" ")
            print(self.name +  " : (move2) Moving to %s" % newPeg)

            self.robotMove(newPeg,RoboMaster)

            RoboMaster.peg = newPeg
            self.peg = newPeg   # Position updated. For when the item is the smallest in the peg
            print("POST-COMPUTATION ----->   self.peg: "+ str(self.peg), "robomaster: " + str(RoboMaster.peg))


# Make 3 discs all on peg 1. 'A' is the largest and on the bottom

def test() :
    ep_robot = robot.Robot()

    try:
        ep_robot.initialize(conn_type='ap')
        Robot = RoboMaster(ep_robot,1)
        c = disc("C",1, None)   # the smallest disc. No nextSmaller disc
        b = disc("B",1, c)      # 2nd largest disc
        a = disc("A",1, b)      # largest disc
        a.move(3,Robot)               # Now move all the discs to peg 3


    except Exception as e:
        print(e)
    ep_robot.close()



if __name__ == "__main__" : test()