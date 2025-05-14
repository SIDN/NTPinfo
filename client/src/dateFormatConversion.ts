export const dateFormatConversion = (time: number): string => {
    const date = new Date(time)
    const iso = date.toISOString()
    return iso.split('.')[0] + 'Z'
}