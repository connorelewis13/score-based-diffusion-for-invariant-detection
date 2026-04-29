package project;

import java.util.Random;
import java.io.FileWriter;
import java.io.IOException;

public class projectile_data {
    public static void main(String[] args) {
        projectile_motion p = new projectile_motion();
        Random rand = new Random();

        try (
            FileWriter trainFw = new FileWriter("data/projectile_train2.csv");
            FileWriter valFw = new FileWriter("data/projectile_val2.csv");
            FileWriter testFw = new FileWriter("data/projectile_test2.csv")
        ) {
            String header = "in_v0,in_angle,out_time,out_max_height,out_final_position\n";
            trainFw.write(header);
            valFw.write(header);
            testFw.write(header);

            int total = 12000;
            int trainCount = 10000;
            int valCount = 1000;

            for (int i = 0; i < total; i++) {
                ProjectileInput input = new ProjectileInput();
                input.v0 = rand.nextDouble() * 10;     // 0 to 10 m/s per proposal
                input.angle = rand.nextDouble() * 180;  // 0 to 180 degrees

                ProjectileOutput output = p.proj_motion_simulator(input);

                String row = input.v0 + "," + input.angle + ","
                           + output.time + "," + output.max_height + "," + output.final_position + "\n";

                if (i < trainCount) trainFw.write(row);
                else if (i < trainCount + valCount) valFw.write(row);
                else testFw.write(row);
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}