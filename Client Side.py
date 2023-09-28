import grpc
import missile_defense_pb2
import missile_defense_pb2_grpc
import time
import random
# from missile_defense_pb2 import Empty

class SoldierClient:
    def __init__(self, soldier_id):
        self.soldier_id = soldier_id
        self.x = random.randint(0, 9)
        self.y = random.randint(0, 9)
        self.speed = random.randint(0, 4)
        self.is_alive = True
        self.channel = grpc.insecure_channel('192.168.1.42:50051')
        self.stub = missile_defense_pb2_grpc.MissileDefenseServiceStub(self.channel)
        self.battlefield = [[' ' for _ in range(10)] for _ in range(10)]

    def missile_approaching(self, position, time, missile_type):
        request = missile_defense_pb2.MissileRequest(
            x=position[0],
            y=position[1],
            time=time,
            type=missile_type,
        )
        self.stub.MissileApproaching(request)

    def status(self):
        request = missile_defense_pb2.SoldierID(id=self.soldier_id)
        response = self.stub.Status(request)
        return response.is_alive

    def was_hit(self):
        request = missile_defense_pb2.SoldierID(id=self.soldier_id)
        self.stub.WasHit(request)
        self.is_alive = False
        print(f"Soldier {self.soldier_id} was hit and is now dead.")

    def take_shelter(self, missile_x, missile_y, missile_type):
        if self.is_alive:
            # Calculate the range of the missile's effect based on missile type
            missile_radius = 0  # Default to no effect
            if missile_type == 1:
                missile_radius = 1
            elif missile_type == 2:
                missile_radius = 2
            elif missile_type == 3:
                missile_radius = 3
            elif missile_type == 4:
                missile_radius = 4

            distance_to_missile = abs(self.x - missile_x) + abs(self.y - missile_y)
            if distance_to_missile <= missile_radius:
                # Calculate the range of the missile's effect on the battlefield
                min_x = max(0, missile_x - missile_radius)
                max_x = min(9, missile_x + missile_radius)
                min_y = max(0, missile_y - missile_radius)
                max_y = min(9, missile_y + missile_radius)

                for y in range(min_y, max_y + 1):
                    for x in range(min_x, max_x + 1):
                        if self.battlefield[y][x] != 'M':
                            self.battlefield[y][x] = 'M'  # Mark the cell with 'M'

                new_x = random.randint(min_x, max_x)
                new_y = random.randint(min_y, max_y)

                if self.battlefield[new_y][new_x] == ' ':
                    self.battlefield[self.y][self.x] = ' '
                    self.x = new_x
                    self.y = new_y
                    self.battlefield[self.y][self.x] = str(self.soldier_id)


    def update_battlefield(self, missile_x, missile_y):
        for soldier_id, soldier in enumerate(soldiers, start=1):
            if soldier.is_alive:
                self.battlefield[soldier.y][soldier.x] = str(soldier_id)
        self.battlefield[missile_y][missile_x] = 'M'  # Mark the missile landing area with 'M'

    def printLayout(self, t, missile_x, missile_y):
        self.update_battlefield(missile_x, missile_y)

        # Print the battlefield
        print(f"Time: {t}")
        print("+" + "-" * 20 + "+")
        for row in self.battlefield:
            print("|" + "|".join(row) + "|")
            print("+" + "-" * 20 + "+")

def commander_behavior():
    commander = SoldierClient(1)
    for t in range(5):  # Simulate 5 time units
        missile_x = random.randint(0, 9)
        missile_y = random.randint(0, 9)
        missile_type = random.randint(1, 4)

        # Broadcast missile approaching
        commander.missile_approaching((missile_x, missile_y), t, missile_type)

        # Simulate soldier behavior
        for soldier in soldiers:
            if soldier.status():
                soldier.take_shelter(missile_x, missile_y, missile_type)

        # Check for battle outcome
        alive_count = sum(1 for soldier in soldiers if soldier.is_alive)
        # if alive_count > len(soldiers) / 2:
        #     print("Battle won!")
        # else:
        #     print("Battle lost!")
        print("Round Over !")

        # Print battlefield layout
        commander.printLayout(t,missile_x, missile_y)
        print("-" * 30)
if __name__ == '__main__':
    soldiers = [SoldierClient(soldier_id) for soldier_id in range(2, 10)]  # Create 9 soldiers
    commander_behavior()
