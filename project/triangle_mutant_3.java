package project;

import java.util.Arrays;

public class triangle_mutant_3 {
    public TriangleOutput triangle_classifier(TriangleInput input) {
        double a = input.a;
        double b = input.b;
        double c = input.c;
        double epsilon = 1e-6;

        TriangleOutput result = new TriangleOutput();

        boolean abEqual = Math.abs(a - b) < epsilon;
        boolean bcEqual = Math.abs(b - c) < epsilon;
        boolean acEqual = Math.abs(a - c) < epsilon;

        if (abEqual && bcEqual) {
            result.type = 3;
        } else if (abEqual || bcEqual || acEqual) {
            result.type = 2;
        } else {
            result.type = 1;
        }

        double[] sides = new double[]{a, b, c};
        Arrays.sort(sides);
        double hyp = sides[2];
        double s1 = sides[0];
        double s2 = sides[1];
        double sumSq = s1*s1 + s2*s2;

        if (Math.abs(sumSq - hyp*hyp) < epsilon) {
            result.angle = 1; //changed 2(right triangle) to acute as a hard one
        } else if (sumSq > hyp*hyp) {
            result.angle = 1;
        } else {
            result.angle = 3;
        }

        return result;
    }
}