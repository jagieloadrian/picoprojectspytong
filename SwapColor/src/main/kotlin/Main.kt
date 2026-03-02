package org.anjo

import java.io.File
import java.io.RandomAccessFile

const val headerSize = 54


fun main(args: Array<String>) {
        val path = args.first()

        val folder = File(path)
        if(!folder.exists() || !folder.isDirectory) {
                println("Incorrect folder: $path")
        }

        val bmpFiles = folder.listFiles {file -> file.extension == "bmp"} ?: return
        bmpFiles.forEach {file ->
                println("Processing: ${file.name}...")
                try {
                        RandomAccessFile(file, "rw").use { raf ->
                                raf.seek(headerSize.toLong())

                                val numPixels = (raf.length() - headerSize) / 2
                                val buf = ByteArray(2)

                                for( i in 0 until numPixels ) {
                                        raf.readFully(buf)
                                        buf[0] = (buf[0].toInt() xor buf[1].toInt()).toByte()
                                        buf[1] = (buf[0].toInt() xor buf[1].toInt()).toByte()
                                        buf[0] = (buf[0].toInt() xor buf[1].toInt()).toByte()

                                        raf.seek(headerSize + i * 2L)
                                        raf.write(buf)
                                }
                        }
                } catch (e:Exception) {
                        println("Error: ${e.message}")
                }
                println("Finished processing ${file.name}...")
        }
}