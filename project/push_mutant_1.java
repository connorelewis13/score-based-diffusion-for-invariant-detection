package project;

public class push_mutant_1 {
    public StackState push_stack(StackState input, int newValue) {
        StackState result = new StackState();
        result.ptr = 1; //always set pointer to 1
        for (int i = 1; i <= 16; i++) result.set(i, input.get(i));
        result.set(result.ptr, newValue);
        return result;
    }
}