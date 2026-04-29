package project;

public class projectile_mutant_6 {
    public ProjectileOutput proj_motion_simulator(ProjectileInput input) {
        double g = 9.81;
        double thetaRad = Math.toRadians(input.angle);
        ProjectileOutput result = new ProjectileOutput();
        result.time = (2 * input.v0 * Math.sin(thetaRad)) / g;
        result.max_height = (input.v0 * input.v0 * Math.pow(Math.sin(thetaRad), 2)) / (2 * g); 
        result.final_position = (input.v0 * input.v0 * Math.cos(2 * thetaRad)) / g; //flipped sin to cos in final position
        return result;
    }
}