package project;

public class pop_mutant_4 {
    public StackState pop_stack(StackState input) {
        StackState result = new StackState();
        result.ptr = input.ptr - 1;
        for (int i = 1; i <= 16; i++) result.set(i, input.get(i));
        result.set(1, 0); //set 1's value to 0 instead to input.ptr's value to 0
        return result;
    }
}