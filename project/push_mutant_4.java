package project;

public class push_mutant_4 {
    public StackState push_stack(StackState input, int newValue) {
        StackState result = new StackState();
        result.ptr = input.ptr+1;
        for (int i = 1; i <= 16; i++) result.set(i, input.get(i));
        result.set(1, newValue); //set 1's value to newvalue instead of new pointer's value
        return result;
    }
}