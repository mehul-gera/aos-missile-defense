import grpc
import time
import random
import missile_defense_pb2
import missile_defense_pb2_grpc
import concurrent.futures  # Import the ThreadPoolExecutor class
class MissileDefenseServicer(missile_defense_pb2_grpc.MissileDefenseServiceServicer):
    def __init__(self):
        self.soldiers = {}
        self.commander = None

    def MissileApproaching(self, request, context):
        # Handle missile approaching broadcast
        print(f"Commander: Missile approaching at ({request.x}, {request.y}) - Type: {request.type} - Time: {request.time}")

        # Notify soldiers to take shelter
        for soldier_id, soldier in self.soldiers.items():
            self.NotifySoldier(soldier, request)

        # Check for battle outcome and update soldier statuses
        alive_count = sum(1 for soldier in self.soldiers.values() if soldier.is_alive)
        if alive_count <= len(self.soldiers) / 2:
            print("Battle lost!")
        return missile_defense_pb2.Empty()

    def Status(self, request, context):
        # Check status of a soldier
        soldier = self.soldiers.get(request.id, None)
        if soldier:
            return missile_defense_pb2.SoldierStatus(is_alive=soldier.is_alive)
        else:
            return missile_defense_pb2.SoldierStatus(is_alive=False)

    def WasHit(self, request, context):
        # Notify that a soldier was hit
        soldier = self.soldiers.get(request.id, None)
        if soldier:
            soldier.is_alive = False
            print(f"Soldier {request.id} was hit and is now dead.")
        return missile_defense_pb2.BoolMessage(value=True)

    def TakeShelter(self, request, context):
        # Handle a soldier taking shelter
        soldier = self.soldiers.get(request.soldier_id, None)
        if soldier:
            distance_to_missile = abs(soldier.x - request.missile_x) + abs(soldier.y - request.missile_y)
            if distance_to_missile <= soldier.speed:
                soldier.x = random.randint(max(0, request.missile_x - soldier.speed), min(9, request.missile_x + soldier.speed))
                soldier.y = random.randint(max(0, request.missile_y - soldier.speed), min(9, request.missile_y + soldier.speed))
        return missile_defense_pb2.Empty()

    def NotifySoldier(self, soldier, missile_request):
        distance_to_missile = abs(soldier.x - missile_request.x) + abs(soldier.y - missile_request.y)
        if distance_to_missile <= soldier.speed:
            shelter_request = missile_defense_pb2.TakeShelterRequest(
                soldier_id=soldier.soldier_id,
                missile_x=missile_request.x,
                missile_y=missile_request.y,
            )
            self.TakeShelter(shelter_request, None)

def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    missile_defense_pb2_grpc.add_MissileDefenseServiceServicer_to_server(MissileDefenseServicer(), server)
    server.add_insecure_port('192.168.1.42:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()