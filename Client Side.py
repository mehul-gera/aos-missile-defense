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
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = missile_defense_pb2_grpc.MissileDefenseServiceStub(self.channel)

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

    def take_shelter(self, missile_x, missile_y):
        request = missile_defense_pb2.TakeShelterRequest(
            soldier_id=self.soldier_id,
            missile_x=missile_x,
            missile_y=missile_y,
        )
        self.stub.TakeShelter(request)

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
                soldier.take_shelter(missile_x, missile_y)

        # Check for battle outcome
        alive_count = sum(1 for soldier in soldiers if soldier.is_alive)
        if alive_count > len(soldiers) / 2:
            print("Battle won!")
        else:
            print("Battle lost!")

        # Print battlefield layout
        print(f"Time: {t}")
        print("-" * 30)

if __name__ == '__main__':
    soldiers = [SoldierClient(soldier_id) for soldier_id in range(2, 10)]  # Create 9 soldiers
    commander_behavior()
