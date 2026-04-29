package project;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class pop_mutant_tester {
    public static void main(String[] args) {
        // 1. Instantiate your 5 mutant classes
        pop_mutant_1 m1 = new pop_mutant_1();
        pop_mutant_2 m2 = new pop_mutant_2();
        pop_mutant_3 m3 = new pop_mutant_3();
        pop_mutant_4 m4 = new pop_mutant_4();

        String header = "in_ptr,in_v1,in_v2,in_v3,in_v4,in_v5,in_v6,in_v7,in_v8,"
                      + "in_v9,in_v10,in_v11,in_v12,in_v13,in_v14,in_v15,in_v16,"
                      + "out_ptr,out_v1,out_v2,out_v3,out_v4,out_v5,out_v6,out_v7,out_v8,"
                      + "out_v9,out_v10,out_v11,out_v12,out_v13,out_v14,out_v15,out_v16\n";

        try (
            // 2. Open the clean test file for reading, and 5 new files for writing
            BufferedReader br = new BufferedReader(new FileReader("data/pop_test2.csv"));
            FileWriter fw1 = new FileWriter("pop_mutant/pop_mutant_1_test.csv");
            FileWriter fw2 = new FileWriter("pop_mutant/pop_mutant_2_test.csv");
            FileWriter fw3 = new FileWriter("pop_mutant/pop_mutant_3_test.csv");
            FileWriter fw4 = new FileWriter("pop_mutant/pop_mutant_4_test.csv");
        ) {
            // Write headers to all mutant output files
            fw1.write(header);
            fw2.write(header);
            fw3.write(header);
            fw4.write(header);

            // Read and discard the header line from the input file
            String line = br.readLine();

            // 3. Process each row in the test set
            while ((line = br.readLine()) != null) {
                String[] columns = line.split(",");
                
                // Parse the 17 input values (in_ptr + in_v1 through in_v16)
                int[] in_arr = new int[17];
                for (int i = 0; i < 17; i++) {
                    in_arr[i] = Integer.parseInt(columns[i]);
                }

                // --- Run for Mutant 1 ---
                StackState in1 = StackState.fromArray(in_arr);
                StackState out1 = m1.pop_stack(in1);
                writeRow(fw1, in_arr, out1.toArray());

                // --- Run for Mutant 2 ---
                // We recreate the StackState each time just in case a mutant 
                // accidentally corrupts the input object during execution.
                StackState in2 = StackState.fromArray(in_arr);
                StackState out2 = m2.pop_stack(in2);
                writeRow(fw2, in_arr, out2.toArray());

                // --- Run for Mutant 3 ---
                StackState in3 = StackState.fromArray(in_arr);
                StackState out3 = m3.pop_stack(in3);
                writeRow(fw3, in_arr, out3.toArray());

                // --- Run for Mutant 4 ---
                StackState in4 = StackState.fromArray(in_arr);
                StackState out4 = m4.pop_stack(in4);
                writeRow(fw4, in_arr, out4.toArray());
            }

            System.out.println("Successfully generated 4 mutant CSVs based on exact pop_test.csv inputs!");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Helper method to keep the main loop clean
    private static void writeRow(FileWriter fw, int[] in_arr, int[] out_arr) throws IOException {
        StringBuilder sb = new StringBuilder();
        
        // Append inputs
        for (int val : in_arr) {
            sb.append(val).append(",");
        }
        
        // Append outputs
        for (int j = 0; j < out_arr.length; j++) {
            sb.append(out_arr[j]);
            if (j < out_arr.length - 1) sb.append(",");
        }
        sb.append("\n");
        
        fw.write(sb.toString());
    }
}