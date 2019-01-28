from jmetal.algorithm.singleobjective.local_search import LocalSearch
from jmetal.operator import BitFlipMutation, PolynomialMutation
from jmetal.problem import OneMax, Sphere
from jmetal.problem.singleobjective.unconstrained import Rastrigin
from jmetal.util.observer import ProgressBarObserver, ObjectivesObserver
from jmetal.util.solution_list import print_function_values_to_file, print_variables_to_file
from jmetal.util.termination_criterion import StoppingByEvaluations

if __name__ == '__main__':
    problem = Rastrigin(10)

    max_evaluations = 50000
    algorithm = LocalSearch(
        problem=problem,
        mutation=PolynomialMutation(1.0 / problem.number_of_variables, 20.0),
        termination_criterion=StoppingByEvaluations(max=max_evaluations)
    )

    objectives_observer = ObjectivesObserver(frequency=1000)
    algorithm.observable.register(observer=objectives_observer)

    algorithm.run()
    result = algorithm.get_result()

    # Save results to file
    print_function_values_to_file(result, 'FUN.'+ algorithm.get_name() + "." + problem.get_name())
    print_variables_to_file(result, 'VAR.' + algorithm.get_name() + "." + problem.get_name())

    print('Algorithm: ' + algorithm.get_name())
    print('Problem: ' + problem.get_name())
    print('Solution: ' + str(result.variables))
    print('Fitness:  ' + str(result.objectives[0]))
    print('Computing time: ' + str(algorithm.total_computing_time))