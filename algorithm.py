from trader import algorithm_thread

@algorithm_thread
def algorithm(ctx):
    print(ctx.active_positions)