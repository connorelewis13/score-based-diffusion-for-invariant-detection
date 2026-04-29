package project;

public class projectile_mutant_5 {
    public ProjectileOutput proj_motion_simulator(ProjectileInput input) {
        double g = 9.81;
        double thetaRad = Math.toRadians(input.angle);
        ProjectileOutput result = new ProjectileOutput();
        result.time = (2 * input.v0 * Math.sin(thetaRad)) / g;
        result.max_height = (input.v0 * input.v0 * Math.pow(Math.cos(thetaRad), 2)) / (2 * g); //flipped sin to cos in max height
        result.final_position = (input.v0 * input.v0 * Math.sin(2 * thetaRad)) / g;
        return result;
    }
}