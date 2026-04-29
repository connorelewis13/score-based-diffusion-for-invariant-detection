package project;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class triangle_mutant_tester {
    public static void main(String[] args) {
        // 1. Instantiate your 8 mutant classes
        triangle_mutant_1 m1 = new triangle_mutant_1();
        triangle_mutant_2 m2 = new triangle_mutant_2();
        triangle_mutant_3 m3 = new triangle_mutant_3();
        triangle_mutant_4 m4 = new triangle_mutant_4();
        triangle_mutant_5 m5 = new triangle_mutant_5();
        triangle_mutant_6 m6 = new triangle_mutant_6();
        triangle_mutant_7 m7 = new triangle_mutant_7();
        triangle_mutant_8 m8 = new triangle_mutant_8();

        // Exact header from your triangle_data file
        String header = "in_a,in_b,in_c,out_type,out_angle\n";

        try (
            // 2. Open clean test file for reading, and 8 new files for writing
            BufferedReader br = new BufferedReader(new FileReader("data/triangle_test2.csv"));
            FileWriter fw1 = new FileWriter("tri_mutant/triangle_mutant_1_test.csv");
            FileWriter fw2 = new FileWriter("tri_mutant/triangle_mutant_2_test.csv");
            FileWriter fw3 = new FileWriter("tri_mutant/triangle_mutant_3_test.csv");
            FileWriter fw4 = new FileWriter("tri_mutant/triangle_mutant_4_test.csv");
            FileWriter fw5 = new FileWriter("tri_mutant/triangle_mutant_5_test.csv");
            FileWriter fw6 = new FileWriter("tri_mutant/triangle_mutant_6_test.csv");
            FileWriter fw7 = new FileWriter("tri_mutant/triangle_mutant_7_test.csv");
            FileWriter fw8 = new FileWriter("tri_mutant/triangle_mutant_8_test.csv")
        ) {
            // Write headers
            fw1.write(header);
            fw2.write(header);
            fw3.write(header);
            fw4.write(header);
            fw5.write(header);
            fw6.write(header);
            fw7.write(header);
            fw8.write(header);

            // Skip the header line
            String line = br.readLine();

            // 3. Process each row
            while ((line = br.readLine()) != null) {
                String[] columns = line.split(",");
                
                // Parse the 3 side lengths
                TriangleInput input = new TriangleInput();
                input.a = Double.parseDouble(columns[0]);
                input.b = Double.parseDouble(columns[1]);
                input.c = Double.parseDouble(columns[2]);

                // --- Run all 8 Mutants ---
                writeRow(fw1, input, m1.triangle_classifier(input));
                writeRow(fw2, input, m2.triangle_classifier(input));
                writeRow(fw3, input, m3.triangle_classifier(input));
                writeRow(fw4, input, m4.triangle_classifier(input));
                writeRow(fw5, input, m5.triangle_classifier(input));
                writeRow(fw6, input, m6.triangle_classifier(input));
                writeRow(fw7, input, m7.triangle_classifier(input));
                writeRow(fw8, input, m8.triangle_classifier(input));
            }

            System.out.println("Successfully generated 8 mutant CSVs based on exact triangle_test.csv inputs!");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Helper method matching your triangle_data.java exact formatting
    private static void writeRow(FileWriter fw, TriangleInput in, TriangleOutput out) throws IOException {
        String row = in.a + "," + in.b + "," + in.c + "," + out.type + "," + out.angle + "\n";
        fw.write(row);
    }
}