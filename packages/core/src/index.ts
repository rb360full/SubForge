export interface ParsedCommand {
    readonly name: string | undefined;
    readonly args: readonly string[];
}

export function parseCommand(argv: readonly string[]): ParsedCommand {
    const [name, ...args] = argv;
    return { name, args };
}

