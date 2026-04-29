package project;

import java.util.Random;
import java.io.FileWriter;
import java.io.IOException;

public class triangle_data {

    static Random rand = new Random();

    static void shuffle(TriangleInput t) {
        double[] sides = new double[]{t.a, t.b, t.c};
        for (int i = 2; i > 0; i--) {
            int j = rand.nextInt(i + 1);
            double tmp = sides[i]; sides[i] = sides[j]; sides[j] = tmp;
        }
        t.a = sides[0]; t.b = sides[1]; t.c = sides[2];
    }

    static TriangleInput randomScalene() {
        while (true) {
            double a = rand.nextDouble() * 99 + 1;
            double b = rand.nextDouble() * 99 + 1;
            double c = rand.nextDouble() * 99 + 1;
            if (a + b > c && a + c > b && b + c > a) {
                double epsilon = 0.000001;
                if (Math.abs(a-b) >= epsilon && Math.abs(b-c) >= epsilon && Math.abs(a-c) >= epsilon) {
                    TriangleInput t = new TriangleInput();
                    t.a = a; t.b = b; t.c = c;
                    return t;
                }
            }
        }
    }

    static TriangleInput randomEquilateral() {
        double s = rand.nextDouble() * 99 + 1;
        TriangleInput t = new TriangleInput();
        t.a = s; t.b = s; t.c = s;
        return t;
    }

    static TriangleInput randomIsoscelesAcute() {
        while (true) {
            double s = rand.nextDouble() * 99 + 1;
            double other = rand.nextDouble() * 99 + 1;
            if (s + s > other && s + other > s) {
                double epsilon = 0.000001;
                if (Math.abs(s - other) >= epsilon) {
                    double[] sides = new double[]{s, s, other};
                    java.util.Arrays.sort(sides);
                    if (sides[0]*sides[0] + sides[1]*sides[1] > sides[2]*sides[2]) {
                        TriangleInput t = new TriangleInput();
                        t.a = s; t.b = s; t.c = other;
                        shuffle(t);
                        return t;
                    }
                }
            }
        }
    }

    static TriangleInput randomIsoscelesObtuse() {
        while (true) {
            double s = rand.nextDouble() * 99 + 1;
            double other = rand.nextDouble() * 99 + 1;
            if (s + s > other && s + other > s) {
                double epsilon = 0.000001;
                if (Math.abs(s - other) >= epsilon) {
                    double[] sides = new double[]{s, s, other};
                    java.util.Arrays.sort(sides);
                    if (sides[0]*sides[0] + sides[1]*sides[1] < sides[2]*sides[2]) {
                        TriangleInput t = new TriangleInput();
                        t.a = s; t.b = s; t.c = other;
                        shuffle(t);
                        return t;
                    }
                }
            }
        }
    }

    static TriangleInput randomIsoscelesRight() {
        double leg = rand.nextDouble() * 99 + 1;
        double hyp = Math.sqrt(2) * leg;
        TriangleInput t = new TriangleInput();
        t.a = leg; t.b = leg; t.c = hyp;
        shuffle(t);
        return t;
    }

    static TriangleInput randomScaleneRight() {
        while (true) {
            double a = rand.nextDouble() * 99 + 1;
            double b = rand.nextDouble() * 99 + 1;
            double c = Math.sqrt(a*a + b*b);
            if (c < 200) {
                double epsilon = 0.000001;
                if (Math.abs(a-b) >= epsilon) {
                    TriangleInput t = new TriangleInput();
                    t.a = a; t.b = b; t.c = c;
                    shuffle(t);
                    return t;
                }
            }
        }
    }

    static TriangleInput randomScaleneObtuse() {
        while (true) {
            TriangleInput t = randomScalene();
            double[] sides = new double[]{t.a, t.b, t.c};
            java.util.Arrays.sort(sides);
            if (sides[0]*sides[0] + sides[1]*sides[1] < sides[2]*sides[2]) return t;
        }
    }

    static TriangleInput randomScaleneAcute() {
        while (true) {
            TriangleInput t = randomScalene();
            double[] sides = new double[]{t.a, t.b, t.c};
            java.util.Arrays.sort(sides);
            if (sides[0]*sides[0] + sides[1]*sides[1] > sides[2]*sides[2]) return t;
        }
    }

    static void writeRow(FileWriter fw, TriangleInput input, TriangleOutput output) throws IOException {
        fw.write(input.a + "," + input.b + "," + input.c + "," + output.type + "," + output.angle + "\n");
    }

    public static void main(String[] args) {
        triangles classifier = new triangles();

        try (
            FileWriter trainFw = new FileWriter("data/triangle_train2.csv");
            FileWriter valFw = new FileWriter("data/triangle_val2.csv");
            FileWriter testFw = new FileWriter("data/triangle_test2.csv")
        ) {
            String header = "in_a,in_b,in_c,out_type,out_angle\n";
            trainFw.write(header);
            valFw.write(header);
            testFw.write(header);

            FileWriter[] writers = {trainFw, valFw, testFw};

            int[][] splitCounts = {
                {1430, 143, 143}, // Equilateral
                {1430, 143, 143}, // Isosceles Acute
                {1430, 143, 143}, // Isosceles Obtuse
                {1430, 143, 143}, // Isosceles Right
                {1430, 143, 143}, // Scalene Right
                {1430, 143, 143}, // Scalene Obtuse
                {1430, 143, 143}  // Scalene Acute
            };

            // 1. equilateral
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[0][w]; i++) {
                    TriangleInput in = randomEquilateral();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

            // 2. isosceles acute
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[1][w]; i++) {
                    TriangleInput in = randomIsoscelesAcute();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

            // 3. isosceles obtuse
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[2][w]; i++) {
                    TriangleInput in = randomIsoscelesObtuse();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

            // 4. isosceles right
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[3][w]; i++) {
                    TriangleInput in = randomIsoscelesRight();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

            // 5. scalene right
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[4][w]; i++) {
                    TriangleInput in = randomScaleneRight();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

            // 6. scalene obtuse
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[5][w]; i++) {
                    TriangleInput in = randomScaleneObtuse();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

            // 7. scalene acute
            for (int w = 0; w < 3; w++)
                for (int i = 0; i < splitCounts[6][w]; i++) {
                    TriangleInput in = randomScaleneAcute();
                    writeRow(writers[w], in, classifier.triangle_classifier(in));
                }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}