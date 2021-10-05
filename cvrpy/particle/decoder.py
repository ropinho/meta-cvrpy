from typing import List
from loggibud.v1.types import CVRPInstance, CVRPSolution, CVRPSolutionVehicle
from cvrpy.pso import Particle

from cvrpy.utils import BoundTransformer, linear_distance

class ParticleDecoder:

    @staticmethod
    def decode(particle: Particle, instance: CVRPInstance) -> CVRPSolution:
        # Delimitar o plano cartesiano
        bounds = BoundTransformer.from_instance(instance)

        # Converter todos os pontos para o espaço entre 0 e 1
        depot = bounds.convert_from_point(instance.origin)
        delivery_points = [bounds.convert_from_point(d.point) for d in instance.deliveries]

        # Separar as duas partes das dimensões
        N = len(instance.deliveries)
        M = int((len(particle.position) - N)/2)
        customers_part = particle.position[:N]
        vehicles_part = particle.position[N:]

        # Ordenar os valores de clientes obtendo os índices
        tuples = [tupl for tupl in enumerate(customers_part)]
        tuples.sort(key=lambda x:x[1])
        customer_priority = [ i for i, _ in tuples]
        print('Prioridade:', customer_priority)

        # Definir os pontos a partir dos valores de veículos
        vehicles_points = [(vehicles_part[i], vehicles_part[i+M]) for i in range(M)]

        # Pra cada ponto de entrega, calcular a distância para os pontos de referência
        vehicle_refs = {point: [] for point in vehicles_points}

        for i, d in enumerate(delivery_points):
            nearest = min(vehicles_points, key=lambda x: linear_distance(d, x))
            vehicle_refs[nearest].append(i)
            pass

        # Criar um objeto de CVRPSolution
        vehicles: List[CVRPSolutionVehicle] = []

        for v in vehicle_refs:
            vehicles.append(
                CVRPSolutionVehicle(
                    origin=instance.origin,
                    deliveries=[instance.deliveries[i] for i in vehicle_refs[v]]
                )
            )
            pass

        return CVRPSolution(instance.name, vehicles=vehicles)