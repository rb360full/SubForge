export interface ParsedCommand {
    readonly name: string | undefined;
    readonly args: readonly string[];
}

export interface CommandDefinition {
    readonly name: string;
    readonly description: string;
    readonly usage: string;
}

export interface CommandContext {
    readonly argv: readonly string[];
    readonly command: ParsedCommand;
    readonly definitions: readonly CommandDefinition[];
}

export interface CommandMatch {
    readonly definition: CommandDefinition | undefined;
    readonly isKnown: boolean;
}

export function parseCommand(argv: readonly string[]): ParsedCommand {
    const [name, ...args] = argv;
    return { name, args };
}

export function createCommandContext(
    argv: readonly string[],
    definitions: readonly CommandDefinition[]
): CommandContext {
    return {
        argv,
        command: parseCommand(argv),
        definitions
    };
}

export function matchCommand(context: CommandContext): CommandMatch {
    const definition = context.definitions.find((entry) => entry.name === context.command.name);
    return {
        definition,
        isKnown: definition !== undefined
    };
}
