package project;

public class projectile_mutant_4 {
    public ProjectileOutput proj_motion_simulator(ProjectileInput input) {
        double g = 9.81;
        double thetaRad = Math.toRadians(input.angle);
        ProjectileOutput result = new ProjectileOutput();
        result.time = (2 * input.v0 * Math.cos(thetaRad)) / g; //flipped sin to cos in time
        result.max_height = (input.v0 * input.v0 * Math.pow(Math.sin(thetaRad), 2)) / (2 * g);
        result.final_position = (input.v0 * input.v0 * Math.sin(2 * thetaRad)) / g;
        return result;
    }
}