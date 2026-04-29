package project;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class projectile_mutant_tester {
    public static void main(String[] args) {
        // 1. Instantiate your 8 mutant classes
        projectile_mutant_1 m1 = new projectile_mutant_1();
        projectile_mutant_2 m2 = new projectile_mutant_2();
        projectile_mutant_3 m3 = new projectile_mutant_3();
        projectile_mutant_4 m4 = new projectile_mutant_4();
        projectile_mutant_5 m5 = new projectile_mutant_5();
        projectile_mutant_6 m6 = new projectile_mutant_6();
        projectile_mutant_7 m7 = new projectile_mutant_7();
        projectile_mutant_8 m8 = new projectile_mutant_8();

        // Exact header from your projectile_data file
        String header = "in_v0,in_angle,out_time,out_max_height,out_final_position\n";

        try (
            // 2. Open clean test file for reading, and 8 new files for writing
            BufferedReader br = new BufferedReader(new FileReader("data/projectile_test2.csv"));
            FileWriter fw1 = new FileWriter("proj_mutant/projectile_mutant_1_test.csv");
            FileWriter fw2 = new FileWriter("proj_mutant/projectile_mutant_2_test.csv");
            FileWriter fw3 = new FileWriter("proj_mutant/projectile_mutant_3_test.csv");
            FileWriter fw4 = new FileWriter("proj_mutant/projectile_mutant_4_test.csv");
            FileWriter fw5 = new FileWriter("proj_mutant/projectile_mutant_5_test.csv");
            FileWriter fw6 = new FileWriter("proj_mutant/projectile_mutant_6_test.csv");
            FileWriter fw7 = new FileWriter("proj_mutant/projectile_mutant_7_test.csv");
            FileWriter fw8 = new FileWriter("proj_mutant/projectile_mutant_8_test.csv")
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
                
                // Parse the 2 inputs
                ProjectileInput input = new ProjectileInput();
                input.v0 = Double.parseDouble(columns[0]);
                input.angle = Double.parseDouble(columns[1]);

                // --- Run Mutant 1 ---
                ProjectileOutput out1 = m1.proj_motion_simulator(input);
                writeRow(fw1, input, out1);

                // --- Run Mutant 2 ---
                ProjectileOutput out2 = m2.proj_motion_simulator(input);
                writeRow(fw2, input, out2);

                // --- Run Mutant 3 ---
                ProjectileOutput out3 = m3.proj_motion_simulator(input);
                writeRow(fw3, input, out3);

                // --- Run Mutant 4 ---
                ProjectileOutput out4 = m4.proj_motion_simulator(input);
                writeRow(fw4, input, out4);

                // --- Run Mutant 5 ---
                ProjectileOutput out5 = m5.proj_motion_simulator(input);
                writeRow(fw5, input, out5);

                // --- Run Mutant 6 ---
                ProjectileOutput out6 = m6.proj_motion_simulator(input);
                writeRow(fw6, input, out6);

                // --- Run Mutant 7 ---
                ProjectileOutput out7 = m7.proj_motion_simulator(input);
                writeRow(fw7, input, out7);

                // --- Run Mutant 8 ---
                ProjectileOutput out8 = m8.proj_motion_simulator(input);
                writeRow(fw8, input, out8);
            }

            System.out.println("Successfully generated 8 mutant CSVs based on exact projectile_test.csv inputs!");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Helper method to format and write the row exactly like the original data generator
    private static void writeRow(FileWriter fw, ProjectileInput in, ProjectileOutput out) throws IOException {
        String row = in.v0 + "," + in.angle + "," 
                   + out.time + "," + out.max_height + "," + out.final_position + "\n";
        fw.write(row);
    }
}