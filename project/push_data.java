package project;

import java.util.Random;
import java.io.FileWriter;
import java.io.IOException;

public class push_data {
    public static void main(String[] args) {
        push p = new push();
        Random rand = new Random();

        try (
            FileWriter trainFw = new FileWriter("data/push_train2.csv");
            FileWriter valFw = new FileWriter("data/push_val2.csv");
            FileWriter testFw = new FileWriter("data/push_test2.csv")
        ) {
            String header = "in_ptr,in_v1,in_v2,in_v3,in_v4,in_v5,in_v6,in_v7,in_v8,"
                          + "in_v9,in_v10,in_v11,in_v12,in_v13,in_v14,in_v15,in_v16,in_newValue,"
                          + "out_ptr,out_v1,out_v2,out_v3,out_v4,out_v5,out_v6,out_v7,out_v8,"
                          + "out_v9,out_v10,out_v11,out_v12,out_v13,out_v14,out_v15,out_v16\n";
            trainFw.write(header);
            valFw.write(header);
            testFw.write(header);

            int total = 12000;
            int trainCount = 10000;
            int valCount = 1000;

            for (int i = 0; i < total; i++) {
                int pointer = rand.nextInt(16); // 0 to 15
                int[] arr = new int[17];
                arr[0] = pointer;
                for (int j = 1; j <= pointer; j++) {
                    arr[j] = rand.nextInt(100) + 1; // 1 to 100
                }
                int newValue = rand.nextInt(100) + 1; // 1 to 100

                StackState input = StackState.fromArray(arr);
                int[] in_arr = input.toArray();
                StackState output = p.push_stack(input, newValue);
                int[] out_arr = output.toArray();

                StringBuilder sb = new StringBuilder();
                for (int val : in_arr) sb.append(val).append(",");
                sb.append(newValue).append(",");
                for (int j = 0; j < out_arr.length; j++) {
                    sb.append(out_arr[j]);
                    if (j < out_arr.length - 1) sb.append(",");
                }
                sb.append("\n");
                String row = sb.toString();

                if (i < trainCount) trainFw.write(row);
                else if (i < trainCount + valCount) valFw.write(row);
                else testFw.write(row);
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}