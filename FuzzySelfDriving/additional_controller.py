import numpy as np
from scipy.integrate import quad

class FuzzyGasController:
    """
    # emtiazi todo
    write all the fuzzify,inference,defuzzify method in this class
    """

    def __init__(self):
        pass
    
    def Fuzzification_close(self, dist):
        
        if dist >= 0 and dist <= 50:
            return -0.02*dist + 1
        return 0
    
    def Fuzzification_moderate(self, dist):
        
        if dist <= 50 and dist >= 40:
            return (dist-40)/10
        if dist >= 50 and dist <= 100:
            return (-1*dist+100)/50
        return 0

    def Fuzzification_far(self, dist):
        
        if dist <= 200 and dist >= 90:
            return (dist-90)/110
        if dist >= 200:
            return 1
        return 0
    
    def Integral_numerator_func(self, x, a, b):
        return x*(a*x+b)
    
    def linear_func(self, x, a, b):
        return a*x+b
    
    def compare_two_line(self, intersection_lines, intersection1, inference, i, j, line_i, line_j, inverse_line_i, inverse_line_j):
        
        integral_numerator = 0
        integral_denumerator = 0
        if inference[i] < intersection_lines[1] and inference[j] > inference[i]:
        
            intersection2 = self.linear_func(inference[i], inverse_line_j[0], inverse_line_j[1])
            integral_numerator = quad(self.Integral_numerator_func, intersection1, intersection2, args=(0,inference[i]))[0]
            integral_denumerator = quad(self.linear_func, intersection1, intersection2, args=(0,inference[i]))[0]
            
            intersection1 = intersection2
            intersection2 = self.linear_func(inference[j], inverse_line_j[0], inverse_line_j[1])
            integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=line_j)[0]
            integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=line_j)[0]
            
            return True, intersection2, integral_numerator, integral_denumerator
        
        elif inference[i] > intersection_lines[1] and inference[j] > intersection_lines[1]:
        
            intersection2 = self.linear_func(inference[i], inverse_line_i[0], inverse_line_i[1])
            integral_numerator = quad(self.Integral_numerator_func, intersection1, intersection2, args=(0,inference[i]))[0]
            integral_denumerator = quad(self.linear_func, intersection1, intersection2, args=(0,inference[i]))[0]
            
            intersection1 = intersection2
            intersection2 = intersection_lines[0]
            integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=line_i)[0]
            integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=line_i)[0]
        
            intersection1 = intersection2
            intersection2 = self.linear_func(inference[j], inverse_line_j[0], inverse_line_j[1])
            integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=line_j)[0]
            integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=line_j)[0]
            
            return True, intersection2, integral_numerator, integral_denumerator
            
        
        return False, intersection1, integral_numerator, integral_denumerator
    
    def integral(self, inference):
        
        intersection_of_lines = [[[7.5, 0.5]], [[105/4, 0.25]]]
        inverse_lines = [(5, 0), (-5, 10), (15, 0), (-15, 30), (-5, 25), (-60, 90)]
        lines = [(0.2, 0), (-0.2, 2), (1/15, 0), (-1/15, 2), (0.2, -5), (-1/60, 90/60)]
        intersection_candidate = [[1], [2]]

        intersection1 = self.linear_func(inference[0], inverse_lines[0][0], inverse_lines[0][1])
        integral_numerator = quad(self.Integral_numerator_func, 0, intersection1, args=lines[0])[0]
        integral_denumerator = quad(self.linear_func, 0, intersection1, args=lines[0])[0]
        
        c2 = 0
        for i in range(2):
            k = 0
            c = 1
            if c2 == 1:
                c2 = 0
                continue
            for j in intersection_candidate[i]:
                b, intersection1, numerator, denumerator = self.compare_two_line(intersection_of_lines[i][k], intersection1, inference, i, j, lines[2*i+1], lines[2*j], inverse_lines[2*i+1], inverse_lines[2*j])
                k += 1
                if b == True:
                    integral_denumerator += denumerator
                    integral_numerator += numerator
                    c = 0
                    if k != 1 and len(intersection_candidate[i]) > 1:
                        c2 = 1
                    break
            if c == 1:
                intersection2 = self.linear_func(inference[i], inverse_lines[2*i+1][0], inverse_lines[2*i+1][1])
                integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=(0, inference[i]))[0]
                integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=(0, inference[i]))[0]
        
                intersection1 = intersection2
                intersection2 = self.linear_func(inference[i+1], inverse_lines[2*i+1][0], inverse_lines[2*i+1][1])
                integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=lines[2*i+1])[0]
                integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=lines[2*i+1])[0]
                intersection1 = intersection2

        intersection2 = self.linear_func(inference[2], inverse_lines[5][0], inverse_lines[5][1])
        integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=(0, inference[2]))[0]
        integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=(0, inference[2]))[0]
        intersection1 = intersection2
        integral_numerator += quad(self.Integral_numerator_func, intersection1, 90, args=lines[5])[0]
        integral_denumerator += quad(self.linear_func, intersection1, 90, args=lines[5])[0]
        
        return integral_numerator/integral_denumerator
        

    def decide(self, center_dist):
        """
        main method for doin all the phases and returning the final answer for gas
        """
        d_C = self.Fuzzification_close(center_dist), self.Fuzzification_moderate(center_dist), self.Fuzzification_far(center_dist)
        inference = d_C[0], d_C[1], d_C[2]
        
        integral = self.integral(inference)
        return integral
    