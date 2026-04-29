package project;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class push_mutant_tester {
    public static void main(String[] args) {
        // 1. Instantiate your 4 mutant classes
        push_mutant_1 m1 = new push_mutant_1();
        push_mutant_2 m2 = new push_mutant_2();
        push_mutant_3 m3 = new push_mutant_3();
        push_mutant_4 m4 = new push_mutant_4();

        // Exact header from your push_data file
        String header = "in_ptr,in_v1,in_v2,in_v3,in_v4,in_v5,in_v6,in_v7,in_v8,"
                      + "in_v9,in_v10,in_v11,in_v12,in_v13,in_v14,in_v15,in_v16,in_newValue,"
                      + "out_ptr,out_v1,out_v2,out_v3,out_v4,out_v5,out_v6,out_v7,out_v8,"
                      + "out_v9,out_v10,out_v11,out_v12,out_v13,out_v14,out_v15,out_v16\n";

        try (
            // 2. Open clean test file for reading, and 4 new files for writing
            BufferedReader br = new BufferedReader(new FileReader("data/push_test2.csv"));
            FileWriter fw1 = new FileWriter("push_mutant/push_mutant_1_test.csv");
            FileWriter fw2 = new FileWriter("push_mutant/push_mutant_2_test.csv");
            FileWriter fw3 = new FileWriter("push_mutant/push_mutant_3_test.csv");
            FileWriter fw4 = new FileWriter("push_mutant/push_mutant_4_test.csv")
        ) {
            // Write headers
            fw1.write(header);
            fw2.write(header);
            fw3.write(header);
            fw4.write(header);

            // Skip the header line
            String line = br.readLine();

            // 3. Process each row
            while ((line = br.readLine()) != null) {
                String[] columns = line.split(",");
                
                // Parse the 17 state inputs
                int[] in_arr = new int[17];
                for (int i = 0; i < 17; i++) {
                    in_arr[i] = Integer.parseInt(columns[i]);
                }
                
                // Parse the 18th column (the value being pushed)
                int newValue = Integer.parseInt(columns[17]);

                // --- Run Mutant 1 ---
                StackState in1 = StackState.fromArray(in_arr);
                StackState out1 = m1.push_stack(in1, newValue);
                writeRow(fw1, in_arr, newValue, out1.toArray());

                // --- Run Mutant 2 ---
                StackState in2 = StackState.fromArray(in_arr);
                StackState out2 = m2.push_stack(in2, newValue);
                writeRow(fw2, in_arr, newValue, out2.toArray());

                // --- Run Mutant 3 ---
                StackState in3 = StackState.fromArray(in_arr);
                StackState out3 = m3.push_stack(in3, newValue);
                writeRow(fw3, in_arr, newValue, out3.toArray());

                // --- Run Mutant 4 ---
                StackState in4 = StackState.fromArray(in_arr);
                StackState out4 = m4.push_stack(in4, newValue);
                writeRow(fw4, in_arr, newValue, out4.toArray());
            }

            System.out.println("Successfully generated 4 mutant CSVs based on exact push_test.csv inputs!");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Updated helper method to include newValue in the output string
    private static void writeRow(FileWriter fw, int[] in_arr, int newValue, int[] out_arr) throws IOException {
        StringBuilder sb = new StringBuilder();
        
        // Append stack inputs
        for (int val : in_arr) {
            sb.append(val).append(",");
        }
        
        // Append newValue
        sb.append(newValue).append(",");
        
        // Append outputs
        for (int j = 0; j < out_arr.length; j++) {
            sb.append(out_arr[j]);
            if (j < out_arr.length - 1) sb.append(",");
        }
        sb.append("\n");
        
        fw.write(sb.toString());
    }
}