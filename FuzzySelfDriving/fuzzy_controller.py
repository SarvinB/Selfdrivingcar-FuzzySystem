import numpy as np
from scipy.integrate import quad

class FuzzyController:
    """
    #todo
    write all the fuzzify,inference,defuzzify method in this class
    """

    def __init__(self):
        pass
    
    def Fuzzification_close(self, left_dist):
        
        if left_dist >= 0 and left_dist <= 50:
            return -0.02*left_dist + 1
        return 0
    
    def Fuzzification_moderate(self, left_dist):
        
        if left_dist <= 50 and left_dist >= 35:
            return (left_dist-35)/15
        if left_dist >= 50 and left_dist <= 65:
            return (-1*left_dist+65)/15
        return 0

    def Fuzzification_far(self, left_dist):
        
        if left_dist >= 50 and left_dist <= 100:
            return 0.02*left_dist-1
        return 0
    
    
    def Fuzzification(self, left_dist,right_dist):
        
        d_L = self.Fuzzification_close(left_dist), self.Fuzzification_moderate(left_dist), self.Fuzzification_far(left_dist)
        d_R = self.Fuzzification_close(right_dist), self.Fuzzification_moderate(right_dist), self.Fuzzification_far(right_dist)
        
        return d_L, d_R
    
    
    def Inference(self, d_L, d_R):
        low_right = min(d_L[0], d_R[1])
        high_right = min(d_L[0], d_R[2])
        low_left = min(d_L[1], d_R[0])
        high_left = min(d_L[2], d_R[0])
        nothing = min(d_L[1], d_R[1])
        
        return high_right, low_right, nothing, low_left, high_left
    
    
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
        
        intersection_of_lines = [[[-14, 0.6], [-8, 0.2]], [[-5, 0.5]], [[5, 0.5], [8, 0.2]], [[14, 0.6]]]
        inverse_lines = [(30, -50), (-15, -5), (10, -20), (-10, 0), (10, -10), (-10, 10), (10, 0), (-10, 20), (15, 5), (-30, 50)]
        lines = [(1/35, 11/7), (-1/15, -1/3), (0.1, 2), (-0.1, 0), (0.1, 1), (-0.1, 1), (0.1, 0), (-0.1, 2), (1/15, -1/3), (-1/35, 11/7)]
        intersection_candidate = [[1, 2], [2], [3, 4], [4]]

        intersection1 = self.linear_func(inference[0], inverse_lines[0][0], inverse_lines[0][1])
        integral_numerator = quad(self.Integral_numerator_func, -50, intersection1, args=lines[0])[0]
        integral_denumerator = quad(self.linear_func, -50, intersection1, args=lines[0])[0]
        
        c2 = 0
        for i in range(4):
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

        intersection2 = self.linear_func(inference[4], inverse_lines[9][0], inverse_lines[9][1])
        integral_numerator += quad(self.Integral_numerator_func, intersection1, intersection2, args=(0, inference[4]))[0]
        integral_denumerator += quad(self.linear_func, intersection1, intersection2, args=(0, inference[4]))[0]
        intersection1 = intersection2
        integral_numerator += quad(self.Integral_numerator_func, intersection1, 50, args=lines[9])[0]
        integral_denumerator += quad(self.linear_func, intersection1, 50, args=lines[9])[0]
        
        return integral_numerator/integral_denumerator
        


    def decide(self, left_dist,right_dist):
        """
        main method for doin all the phases and returning the final answer for rotation
        """
        
        d_L, d_R = self.Fuzzification(left_dist, right_dist)
        inference = self.Inference(d_L, d_R)
        
        integral = self.integral(inference)
        return integral

    
    