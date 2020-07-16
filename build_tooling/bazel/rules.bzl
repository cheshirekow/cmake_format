def _glslang_compile_impl(ctx):
  src = ctx.attr.src.files.to_list()[0]
  out = ctx.actions.declare_file(ctx.attr.out)

  cmd = "glslangValidator -V -o {out} {src}".format(
    out = out.path,
    src = src.path,
  )

  ctx.actions.run_shell(
    outputs = [out],
    inputs = [src],
    command = cmd,
    mnemonic = "glslangValidator",
    use_default_shell_env = True,
  )

  return [DefaultInfo(files = depset([out]))]

glslang_compile = rule(
  _glslang_compile_impl,
  attrs = {
    "src": attr.label(
      allow_files = [".vert", ".frag"],
      doc = "Source file to compile into binary",
    ),
    "out": attr.string(
      #allow_files=[".spv"],
      doc = "Output file to generate",
    ),
  },
  doc = "Compile one or more glsl files into SPIR-V",
)
